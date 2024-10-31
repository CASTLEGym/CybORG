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
from torch.optim import Adam
from torch.distributions.categorical import Categorical
from torch_geometric.nn import GCNConv

N_HOSTS = 13
N_HOST_ACTIONS = 11  # Analyze, remove, restore, decoy*8
N_GLOBAL_ACTIONS = 2 # Sleep & monitor
ACTION_SPACE = (N_HOST_ACTIONS*N_HOSTS) + N_GLOBAL_ACTIONS

class PPOMemory:
    def __init__(self, bs):
        self.s = []
        self.a = []
        self.v = []
        self.p = []
        self.r = []
        self.t = []

        self.bs = bs

    def remember(self, s,a,v,p,r,t):
        '''
        Can ignore is_terminal flag for CAGE since episodes continue forever
        (may need to revisit if TA1 does something different)

        Args are state, action, value, log_prob, reward
        '''
        self.s.append(s)
        self.a.append(a)
        self.v.append(v)
        self.p.append(p)
        self.r.append(r)
        self.t.append(t)

    def clear(self):
        self.s = []; self.a = []
        self.v = []; self.p = []
        self.r = []; self.t = []

    def get_batches(self):
        idxs = torch.randperm(len(self.a))
        batch_idxs = idxs.split(self.bs)

        return self.s, self.a, self.v, \
            self.p, self.r, self.t, batch_idxs


class ActorNetwork(nn.Module):
    def __init__(self, in_dim, num_nodes=N_HOSTS, action_space=ACTION_SPACE,
                 hidden1=256, hidden2=64, lr=0.0003):
        super().__init__()

        self.conv1 = GCNConv(in_dim, hidden1)
        self.conv2 = GCNConv(hidden1, hidden2)
        self.out = nn.Sequential(
            nn.Linear(hidden2*num_nodes, action_space),
            nn.Softmax(dim=-1)
        )

        self.drop = nn.Dropout()
        self.opt = Adam(self.parameters(), lr)
        self.num_nodes = num_nodes

    def forward(self, x, ei):
        hosts = x[:, 0] == 1

        x = torch.relu(self.conv1(x, ei))
        x = torch.relu(self.conv2(x, ei))

        host_z = x[hosts]
        nbatches = host_z.size(0) // self.num_nodes
        dist = self.out(host_z.reshape(nbatches, self.num_nodes*host_z.size(1)))

        return Categorical(dist)


class CriticNetwork(nn.Module):
    def __init__(self, in_dim, num_nodes=N_HOSTS, hidden1=256,
                 hidden2=64, lr=0.001):
        super().__init__()

        self.conv1 = GCNConv(in_dim, hidden1)
        self.conv2 = GCNConv(hidden1, hidden2)
        self.out = nn.Linear(hidden2*num_nodes, 1)

        self.opt = Adam(self.parameters(), lr)
        self.num_nodes = num_nodes

    def forward(self, x, ei):
        hosts = x[:, 0] == 1

        x = torch.relu(self.conv1(x, ei))
        x = torch.relu(self.conv2(x, ei))

        host_z = x[hosts]
        nbatches = host_z.size(0) // self.num_nodes
        return self.out(host_z.reshape(nbatches, self.num_nodes*host_z.size(1)))


class ActorCritic(nn.Module):
    def __init__(self, in_dim, num_nodes=N_HOSTS, action_space=ACTION_SPACE,
                 hidden1=256, hidden2=64, lr=0.001):
        super().__init__()

        self.conv1 = GCNConv(in_dim, hidden1)
        self.conv2 = GCNConv(hidden1, hidden2)

        self.critic_net = nn.Linear(hidden2*num_nodes, 1)
        self.actor_net = nn.Sequential(
            nn.Linear(hidden2*num_nodes, action_space),
            nn.Softmax(dim=-1)
        )

        self.opt = Adam(self.parameters(), lr=lr)

    def forward(self, x,ei):
        z = self.embed(x,ei)
        value = self.critic_net(z)
        distro = Categorical(self.actor_net(z))

        return value,distro

    def embed(self, x,ei):
        hosts = x[:, 0] == 1

        # Generate shared node embedding representations
        z = torch.relu(self.conv1(x,ei))
        z = torch.relu(self.conv2(z,ei))

        return z[hosts].flatten()

    def policy(self, x,ei):
        z = self.embed(x,ei)
        distro = Categorical(self.actor_net(z))
        return distro

    def value(self, x,ei):
        z = self.embed(x,ei)
        value = self.critic_net(z)
        return value


class GraphPPOAgent:
    def __init__(self, in_dim, gamma=0.99, lmbda=0.95, clip=0.1, bs=5, epochs=6,
                 a_kwargs=dict(), c_kwargs=dict(), training=True):
        self.actor = ActorNetwork(in_dim, **a_kwargs)
        self.critic = CriticNetwork(in_dim, **c_kwargs)
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

        self.training = training
        self.deterministic = False
        self.mse = nn.MSELoss()

    def set_deterministic(self, val):
        self.deterministic = val

    def train(self):
        self.training = True
        self.actor.train()
        self.critic.train()

    def eval(self):
        self.training = False
        self.actor.eval()
        self.critic.eval()

    def save(self, outf='saved_models/graph_ppo.pt'):
        me = (self.args, self.kwargs)

        torch.save({
            'actor': self.actor.state_dict(),
            'critic': self.critic.state_dict(),
            'agent': me
        }, outf)

    def remember(self, s,a,v,p,r,t):
        self.memory.remember(s,a,v,p,r,t)

    def end_episode(self):
        pass

    @torch.no_grad()
    def get_action(self, x_ei):
        x,ei = x_ei
        distro = self.actor(x,ei)

        # I don't know why this would ever be called
        # during training, but just in case, putting the
        # logic block outside the training check
        if self.deterministic:
            action = distro.probs.argmax()
        else:
            action = distro.sample()

        if not self.training:
            return action.item()

        value = self.critic(x,ei)
        prob = distro.log_prob(action)
        return action.item(), value.item(), prob.item()

    def learn(self, verbose=True):
        '''
        Assume that an external process is adding memories to
        the PPOMemory unit, and this is called every so often
        '''
        for e in range(self.epochs):
            s,a,v,p,r,t, batches = self.memory.get_batches()

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
                batched_states = combine_subgraphs(s_)
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

    def _zero_grad(self):
        self.actor.opt.zero_grad()
        self.critic.opt.zero_grad()

    def _step(self):
        self.actor.opt.step()
        self.critic.opt.step()


def load_pretrained(in_f='model_weights/noninductive.pt'):
    data = torch.load(in_f)

    args,kwargs = data['agent']
    agent = GraphPPOAgent(*args, **kwargs)
    agent.actor.load_state_dict(data['actor'])
    agent.critic.load_state_dict(data['critic'])

    agent.eval()
    return agent


def combine_subgraphs(states, uneven_batches=False):
    xs,eis = zip(*states)

    # ei we need to update each node idx to be
    # ei[i] += len(ei[i-1])
    offset=0
    new_eis=[]
    batches=[0]
    for i in range(len(eis)):
        new_eis.append(eis[i]+offset)

        if uneven_batches:
            n_hosts = (xs[i][:, 0] == 1).sum()
            batches.append(batches[-1] + n_hosts)

        offset += xs[i].size(0)

    # X is easy, just cat
    xs = torch.cat(xs, dim=0)
    eis = torch.cat(new_eis, dim=1)

    if uneven_batches:
        return xs, eis, torch.tensor(batches)
    return xs,eis