#this is not yet functional. Need to add some functionality to shuffle the deck so cant just choose the future
from treys import Card, Evaluator, Deck
from itertools import combinations
from copy import deepcopy
import time
import random

HAND_SIZE = 5
COMBINATIONS = 2**HAND_SIZE
SIMULATIONS = 50
AVAILABLE_ACTIONS = list(range(COMBINATIONS))

class Poker():
    #constructor
    def __init__(self):
        self.deck = None
        self.botHand = None
        self.humanHand = None
        self.evaluator = Evaluator()
        
        
    #reset hand and deck
    def reset(self):
        self.deck = Deck()
        self.botHand = self.drawACard(HAND_SIZE)
        return self.botHand

    #return ints [0, 31] as action space is constant regardless of initial state
    def available_actions(self):
        return AVAILABLE_ACTIONS
        

    #convert any action (integer [0,31] to a binary representation)
    #ex: 2 -> 00010 and corresponds to discarding fourth card and keeping all others
    def intToFiveBitBinary(self, number):
        if not 0 <= number <= COMBINATIONS-1:
            return "error"
        
        binary_string = f'{number:05b}'
        return binary_string


    #discard specified cards and replace them with new cards
    def move(self, action):
        binaryAction = self.intToFiveBitBinary(action)
        newHand = []
        
        for i in range(HAND_SIZE):
            if binaryAction[i] == "0":
                newHand.append(self.botHand[i])
        
        discardCount = HAND_SIZE - len(newHand)
        for i in range(discardCount):
            newHand.append(self.drawACard(1)[0])

        self.botHand = newHand
        return self.botHand
    

    #save a state to be accesses after a simulation
    def saveState(self):
        return self.botHand.copy(), list(self.deck.cards)

    #restore a state after a simulation
    def restore(self, saveState):
        self.botHand, deckCards = saveState
        self.deck.cards = list(deckCards)
        
    

    def drawACard(self, n=1):
        drawn=[]
        for i in range(n):
            index = random.randrange(len(self.deck.cards))
            drawn.append(self.deck.cards.pop(index))
        return drawn

    
        


class PokerAI():
    def __init__(self, simulations=SIMULATIONS):
        self.simulations = simulations
        self.evaluator = Evaluator()

    #Figure out best action for first turn of discard
    def bestFirstDiscard(self, pokerEnv, redraws = 2):
        bestAction = None
        bestValue = float('inf')

        #simulate all actions in action space to find the best one
        for action in pokerEnv.available_actions():
            averageValue = self.simulate(pokerEnv, action, redraws)
            if averageValue < bestValue:
                bestValue = averageValue
                bestAction = action

        
        return bestAction

    def simulate(self, pokerEnv, action, redraws):

        totalValue = 0

        saveState = pokerEnv.saveState()

        for i in range(self.simulations):

            #create copy for simulations
            pokerEnv.restore(saveState)

            #take action, and update hand in pokerEnvCopy
            new_hand = pokerEnv.move(action)

            #must base best decision for first redraw on outcomes of second redraw
            if redraws > 1:
                secondAction = self.bestSecondActionMonteCarlo(pokerEnv)
                new_hand = pokerEnv.move(secondAction)

            #add value of hand
            totalValue += self.evaluator._five(new_hand)

        pokerEnv.restore(saveState)

        #return approximate ev of action
        return totalValue / self.simulations

    
    #Calculate the best action on the second round of discards
    def bestSecondActionMonteCarlo(self, pokerEnv):
        bestAction = None
        bestValue = float('inf')

        saveState = pokerEnv.saveState()
        #simulate all possible actions
        for action in pokerEnv.available_actions():
            totalValue = 0

            for i in range(self.simulations):
                #save current state for next simulation
                pokerEnv.restore(saveState)

                #evaluate action
                new_hand = pokerEnv.move(action)
                totalValue += self.evaluator._five(new_hand)

                #restore original state for next simulation
                pokerEnv.restore(saveState)
            
            averageValue = totalValue / self.simulations


            if averageValue < bestValue:
                bestValue = averageValue
                bestAction = action
            
            pokerEnv.restore(saveState)

        return bestAction
    

    


def main():

    #Go through the bots turns first so that the user's cards are not taken out of deck and factored into simulation. The point of this is to keep the game fair / equal information
    poker = Poker()
    pokerAI = PokerAI(simulations=SIMULATIONS)  # keep low for testing
    
    humanChips = 100
    botChips = 100
    while (humanChips>0 and botChips>0):
        print("\n\n\n")
        print(f"Chip Counts | Human: {humanChips} | Bot: {botChips}\n")
        wagerAmount = float('inf')
        while (wagerAmount > humanChips or wagerAmount > botChips):
            wagerAmount = int(input("How many chips would like like to wager on this hand? "))

        originalBotHand = poker.reset()
        originalBotScore =  poker.evaluator._five(originalBotHand)
        originalBotRank = poker.evaluator.get_rank_class(originalBotScore)
        
        first_action = pokerAI.bestFirstDiscard(poker, redraws = 2)
        

        middleBotHand = poker.move(first_action)
        middleBotScore =  poker.evaluator._five(middleBotHand)
        middleBotRank = poker.evaluator.get_rank_class(middleBotScore)

        second_action = pokerAI.bestSecondActionMonteCarlo(poker)

        finalBotHand = poker.move(second_action)

        botScore = poker.evaluator._five(finalBotHand)
        botRank = poker.evaluator.get_rank_class(botScore)

        #now that the bot has made its turns, human is going to go through their turns
        #it is ok that the human goes after the bot, since cards have equal probability of being anywhere in deck.
        humanHand = poker.drawACard(5)
        print("Your Starting Hand:\n")
        print([Card.int_to_str(c) for c in humanHand])
        humanScore = poker.evaluator._five(humanHand)
        humanRank = poker.evaluator.get_rank_class(humanScore)
        print(poker.evaluator.class_to_string(humanRank))
        

        #Round 1 of discarding for human
        userChoice = input("\nRound 1: Enter indices of card to discard, [0,4], separated by spaces: ").split()
        newHumanHand = []
        
        for i in range(HAND_SIZE):
            if not str(i) in userChoice:
                newHumanHand.append(humanHand[i])
            else:
                newHumanHand.append(poker.drawACard(1)[0])
        time.sleep(1.5)
        print("\nNew Hand:\n")
        print([Card.int_to_str(c) for c in newHumanHand])
        humanScore = poker.evaluator._five(newHumanHand)
        humanRank = poker.evaluator.get_rank_class(humanScore)
        print(poker.evaluator.class_to_string(humanRank))

        #Round 2 of discarding for human
        userChoice = input("\nRound 2: Enter indices of card to discard, [0,4], separated by spaces: ").split()
        finalHumanHand = []
        for i in range(HAND_SIZE):
            if not str(i) in userChoice:
                finalHumanHand.append(newHumanHand[i])
            else:
                finalHumanHand.append(poker.drawACard(1)[0])

        #Print User Hand
        time.sleep(1.5)
        print("\nFinal Hand:\n")
        print([Card.int_to_str(c) for c in finalHumanHand])
        
        humanScore = poker.evaluator._five(finalHumanHand)
        humanRank = poker.evaluator.get_rank_class(humanScore)

        print("\nYour Hand Rank: ", poker.evaluator.class_to_string(humanRank))
        time.sleep(1.5)
        
        #print out bot hand trajectory
        print("\nNow you will see if you beat the bot")
        for i in range(5):
            print(".")
            time.sleep(0.5)

        print("\nOriginal Bot Hand: \n")
        print([Card.int_to_str(c) for c in originalBotHand])
        print(poker.evaluator.class_to_string(originalBotRank))
        if humanScore < originalBotScore:
            print("\nHuman Ahead")
        elif humanScore > originalBotScore:
            print("\nBot Ahead")
        else:
            print("\nCurrently tied")
        time.sleep(3)

        print("\nBot Hand After One Round: \n")
        print([Card.int_to_str(c) for c in middleBotHand])
        print(poker.evaluator.class_to_string(middleBotRank))
        if humanScore < middleBotScore:
            print("\nHuman Ahead")
        elif humanScore > middleBotScore:
            print("\nBot Ahead")
        else:
            print("\nCurrently tied")
        time.sleep(3)

        print("\n\n\nFinal Bot Hand: \n")
        print([Card.int_to_str(c) for c in finalBotHand])
        print("\nFinal HumanHand:\n")
        print([Card.int_to_str(c) for c in finalHumanHand])
        time.sleep(3)
        
        print("\n")

        #let user know who won
        if humanScore < botScore:
            print(f"Human's {poker.evaluator.class_to_string(humanRank)} beats bot's {poker.evaluator.class_to_string(botRank)}")
            humanChips += wagerAmount
            botChips -= wagerAmount
        elif humanScore > botScore:
            print(f"Bots's {poker.evaluator.class_to_string(botRank)} beats humans's {poker.evaluator.class_to_string(humanRank)}")
            humanChips -= wagerAmount
            botChips += wagerAmount
        else:
            print(f"Chopped pot: Two equal {poker.evaluator.class_to_string(humanRank)}s")

    

    if humanChips == 0:
        print("\n\n\nBot Wins the Heads Up Match")
    else:
        print("\n\n\nHuman Wins the Heads Up Match")



if __name__ == "__main__":
    main()

