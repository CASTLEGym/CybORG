# Cybermonic CASTLE KEEP Agent
# Copyright (C) 2024 Cybermonic LLC

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import torch
from torch import nn
from torch.distributions import Categorical
from torch.optim import Adam
from torch_geometric.nn import GCNConv



def pad_and_pack(x, batches, max_batch=None):
    n_batches = batches.size(0)-1
    if max_batch is None:
        max_batch = (batches[1:] - batches[:-1]).max()

    out = torch.zeros(n_batches, max_batch, x.size(-1)) # B x S x d
    mask = torch.zeros(n_batches, max_batch, 1)

    for i in range(n_batches):
        st = batches[i]; en = batches[i+1]
        tot = en-st
        out[i][:tot] = x[st:en]
        mask[i][:tot] = 1.

    return out,mask


class SimpleSelfAttention(nn.Module):
    '''
    Implimenting global-node self-attention from
        https://arxiv.org/pdf/2009.12462.pdf
    '''
    def __init__(self, in_dim, h_dim, g_dim):
        super().__init__()

        self.att = nn.Sequential(
            nn.Linear(in_dim, h_dim),
            nn.Softmax(dim=-1)
        )
        self.feat = nn.Linear(in_dim, h_dim)
        self.glb = nn.Linear(h_dim+g_dim, g_dim)

        self.g_dim = g_dim
        self.h_dim = h_dim

    def forward(self, v, mask=None, g=None):
        '''
        Inputs:
            v: B x N x d tensor
            g: B x d tensor
        '''
        if g is None:
            g = torch.zeros((v.size(0), self.g_dim))
        if mask is None:
            mask = torch.ones((v.size(0), v.size(1), 1))

        att = self.att(v)               # B x N x h
        att = att * mask                # Zero out any masked rows
        feat = self.feat(v)             # B x N x h
        out = (att*feat).sum(dim=1)     # B x h

        g_ = self.glb(torch.cat([out,g], dim=-1))  # B x g
        return g + g_                               # Short-circuit


class GlobalNodeInductiveActorNetwork(nn.Module):
    def __init__(self, in_dim, action_space=11, n_global_actions=2,
                 hidden1=256, hidden2=64, lr=0.0003, **kwargs):
        super().__init__()
        self.N_GLOBAL_ACTIONS = n_global_actions
        self.N_NODE_ACTIONS = action_space

        gdim = hidden1
        self.out = nn.Sequential(
            nn.Linear(hidden2+gdim, hidden1),
            nn.ReLU(),
            nn.Linear(hidden1, action_space)
        )

        self.g0_attn = SimpleSelfAttention(in_dim, hidden1, gdim)
        self.g1_attn = SimpleSelfAttention(hidden1, hidden1, gdim)
        self.g2_attn = SimpleSelfAttention(hidden2, hidden2, gdim)

        self.conv1 = GCNConv(in_dim, hidden1)
        self.conv2 = GCNConv(hidden1, hidden2)

        self.opt = Adam(self.parameters(), lr)

    def forward(self, x, ei, batches=None):
        '''
        x:          |V| x d node feature matrix
        ei:         2 x |E| edge index
        batches:    CSR style index of where batches start and end.
                    E.g. for 3 graphs with 3,4 and 2 nodes would be
                        [0,3,7,9]
                    Note: this is for x[hosts], not x
        '''
        hosts = x[:, 0] == 1

        # Assume unbatched input. E.g. single graph
        if batches is None:
            batches = torch.tensor([0, hosts.sum()], dtype=torch.long)

        batch_sizes = batches[1:] - batches[:-1]
        max_batch = batch_sizes.max()

        z,mask = pad_and_pack(x[hosts], batches, max_batch)
        g = self.g0_attn(z,mask=mask)
        x = torch.relu(self.conv1(x, ei))

        z,mask = pad_and_pack(x[hosts], batches, max_batch)
        g = self.g1_attn(z, mask=mask, g=g) # B x h2
        x = torch.relu(self.conv2(x, ei))

        z,mask = pad_and_pack(x[hosts], batches, max_batch)
        g = self.g2_attn(z, mask=mask, g=g)             # B x h2
        g = g.repeat_interleave(batch_sizes, 0)         # B*N x h2

        host_z = torch.cat([x[hosts], g], dim=1)        # B*N x h2*2
        actions = self.out(host_z)                      # B*N x a

        # Group by p(a) (currently grouped by node id)
        # B x N_max x a
        out,mask = pad_and_pack(actions, batches, max_batch)
        out[mask.squeeze(-1) == 0] = float('-inf') # Mask actions on nodes that don't exist
        #out = out.transpose(1,2) # Make rows actions, and columns nodes (B x a x N_max)
        out = out.reshape(out.size(0), actions.size(1)*max_batch) # Combine batches into individual rows

        return Categorical(logits=out)


class GlobalNodeInductiveCriticNetwork(nn.Module):
    def __init__(self, in_dim,
                 hidden1=256, hidden2=64, lr=0.001, **kwargs):
        super().__init__()
        gdim = hidden1

        self.out = nn.Sequential(
            nn.Linear(gdim, hidden2),
            nn.ReLU(),
            nn.Linear(hidden2, 1)
        )

        # Changing to maxpooling to mirror paper
        self.conv1 = GCNConv(in_dim, hidden1, aggr='max')
        self.conv2 = GCNConv(hidden1, hidden2, aggr='max')

        self.g0_attn = SimpleSelfAttention(in_dim, hidden1, gdim)
        self.g1_attn = SimpleSelfAttention(hidden1, hidden1, gdim)
        self.g2_attn = SimpleSelfAttention(hidden2, hidden2, gdim)

        self.opt = Adam(self.parameters(), lr)

    def forward(self, x, ei, batches=None):
        hosts = x[:, 0] == 1

        # Assume unbatched input. E.g. single graph
        if batches is None:
            batches = torch.tensor([0, hosts.sum()], dtype=torch.long)

        n_batches = batches[1:] - batches[:-1]
        max_batch = n_batches.max()

        h,mask = pad_and_pack(x[hosts], batches, max_batch)
        g = self.g0_attn(h, mask=mask)
        x = torch.relu(self.conv1(x, ei))   # B*N x h1

        h,mask = pad_and_pack(x[hosts], batches, max_batch)
        g = self.g1_attn(h, mask=mask, g=g) # B x h2
        x = torch.relu(self.conv2(x, ei))   # B*N x h2

        h,mask = pad_and_pack(x[hosts], batches, max_batch)
        g = self.g2_attn(h, g=g) # B x h2
        return self.out(g)       # B x 1


class InductiveGraphPPOAgent(GraphPPOAgent):
    def __init__(self, in_dim, gamma=0.99, lmbda=0.95, clip=0.1, bs=5, epochs=6,
                 a_kwargs=dict(), c_kwargs=dict(), training=True):

        self.actor = GlobalNodeInductiveActorNetwork(in_dim, **a_kwargs)
        self.critic = GlobalNodeInductiveCriticNetwork(in_dim, **c_kwargs)

        self.memory = PPOMemory(bs)

        self.args = (in_dim,)
        self.kwargs = dict(
            gamma=gamma, lmbda=lmbda, clip=clip, bs=bs, epochs=epochs,
            a_kwargs=a_kwargs, c_kwargs=c_kwargs, training=training
        )

        self.gamma = gamma
        self.lmbda = lmbda
        self.clip = clip
        self.bs = bs
        self.epochs = epochs

        self.action_space = self.actor.N_NODE_ACTIONS

        self.training = training
        self.deterministic = False
        self.mse = nn.MSELoss()


    def learn(self, verbose=True):
        '''
        Same as before, just need to use uneven_batches=True in the combine_subgraphs function
        '''
        for e in range(self.epochs):
            s,a,v,p,r,t, batches = self.memory.get_batches()

            '''
            advantage = torch.zeros(len(s), dtype=torch.float)

            # Probably a more efficient way to do this in parallel w torch
            for t in range(len(s)-1):
                discount = 1
                a_t = 0
                for k in range(t, len(s)-1):
                    a_t += discount*(r[k] + self.gamma*v[k+1] -v[k])
                    discount *= self.gamma*self.lmbda

                advantage[t] = a_t
            '''
            rewards = []
            discounted_reward = 0
            for reward, is_terminal in zip(reversed(r), reversed(t)):
                if is_terminal:
                    discounted_reward = 0
                discounted_reward = reward + self.gamma * discounted_reward
                rewards.insert(0, discounted_reward)

            r = torch.tensor(rewards, dtype=torch.float)
            r = (r - r.mean()) / (r.std() + 1e-5) # Normalize rewards

            advantages = r - torch.tensor(v)

            for b_idx,b in enumerate(batches):
                b = b.tolist()
                new_probs = []

                s_ = [s[idx] for idx in b]
                a_ = [a[idx] for idx in b]
                batched_states = combine_subgraphs(s_, uneven_batches=True)
                dist = self.actor(*batched_states)

                critic_vals = self.critic(*batched_states)
                new_probs = dist.log_prob(torch.tensor(a_))
                old_probs = torch.tensor([p[i] for i in b])
                entropy = dist.entropy()

                a_t = advantages[b]

                # Equiv to exp(new) / exp(old) b.c. recall: these are log probs
                r_theta = (new_probs - old_probs).exp()
                clipped_r_theta = torch.clip(
                    r_theta, min=1-self.clip, max=1+self.clip
                )

                # Use whichever one is minimal
                actor_loss = torch.min(r_theta*a_t, clipped_r_theta*a_t)
                actor_loss = -actor_loss.mean()

                # Critic uses MSE loss between expected value of state and observed
                # reward with discount factor
                critic_loss = self.mse(r[b].unsqueeze(-1), critic_vals)

                # Not totally necessary but maybe will help?
                entropy_loss = entropy.mean()

                # Calculate gradient and backprop
                total_loss = actor_loss + 0.5*critic_loss - 0.01*entropy_loss
                self._zero_grad()
                total_loss.backward()
                self._step()

                if verbose:
                    print(f'[{e}] C-Loss: {0.5*critic_loss.item():0.4f}  A-Loss: {actor_loss.item():0.4f} E-loss: {-entropy_loss.item()*0.01:0.4f}')

        # After we have sampled our minibatches e times, clear the memory buffer
        self.memory.clear()
        return total_loss.item()


def load_agent(in_f='model_weights/inductive_agent.pt'):
    data = torch.load(in_f)
    args,kwargs = data['agent']

    agent = InductiveGraphPPOAgent(*args, **kwargs)
    agent.actor.load_state_dict(data['actor'])
    agent.critic.load_state_dict(data['critic'])

    agent.eval()
    return agent
