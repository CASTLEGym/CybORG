### Model weights

The weights in this folder will work in the `keep_agent`. Models were trained against the BLine and Meander agents for 10,000 epochs, each consisting of 100 episodes. The `inductive_agent` used the default rewards, while the `high_precision` agent (will be available soon) used reward shaping to penalize incorrect Restore and Remove actions. Both agents get about -58 points across 30,50, and 100-step episodes.
