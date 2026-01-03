This file contains a monte carlo simulation based poker AI bot to play 5 card draw:

5 Card Draw: The version of poker that is played in this project is five card draw. The only round of betting ocurrs before cards are seen (an ante), and then players receive five cards. From these five cards, players can discard any of them [0,5], and receive replacement cards.
Then, players get to discard and receive new cards a second time, after which a showdown occurs and the best hand wins. Therefore, the strategy in this game is choosing the optimal cards in each round to discard to maximize expected value of your hand.

This poker bot works by simulating all possible actions. At the first round of discarding, it considers all 32 possible options (from discarding no cards to discarding all cards), and it runs 50 simulations for each of these possibilities. The hand is not yet over, howeover, 
so for each of these simulations it once again considers all of the possible actions and runs 50 simulations for each, resulting in final hands. Then, it works backwards to calculate the expected value of each first round discard decision, and it chooses the decision with the
highest average value. (highest approximated expected value).
For the second round of discarding, it simply has to run 50 simulations of all 32 possible choices, and choose the highest average value choice. 

There is functionality in this program that allows the user to play vs. the AI using command-line input. See if you can beat the optimal AI!
