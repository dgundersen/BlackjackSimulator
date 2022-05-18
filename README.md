# BlackjackSimulator
Designed to run simulations of many blackjack games, specifically including a bust bonus and 21+3 bonus found in casinos in Black Hawk, CO.

![bj_bonuses](https://user-images.githubusercontent.com/13021132/159364862-15cc5e33-c5e5-4b38-b1af-24afd873a839.jpg)

### Bust Bonus

The player is allowed to make a side bet, after the cards are dealt, that pays out if the dealer busts.  The suited payouts require all of the dealer's cards to be of the same suit.

So, for example, the dealer has an up card of 6 and busts on 6 Q 9 non-suited then the bet pays even money.

If the dealer busts with a suited 8 8 8 then the bet pays 75:1.

### 21+3 Bonus

The side bet is placed before the deal.  After the cards are dealt, if your 2 cards and the dealer's up card make one of the hands listed then the bet pays out.  

For example, if you have a 6 7 and the dealer's up card is an 8 then the bet pays 10:1.

## Should I Play The Bonuses?

My wife and I were discussing the merits of the bonuses and whether or not they make sense to play.  She plays the 21+3 bonus while I generally avoid it.  We both play the bust bonus--usually on 2 through 6 and A--as it seems like it helps, but does it?

It's safe to assume that the casino would only offer these bonuses if they were in the house's favor.  So then the questions to be answered are:

1. What is the house's edge on these side bets?
2. Does it ever make sense for the player to play them?

## The Goal

I wrote this simulator to see just how good or bad these bets really are.  The simulator supports different configurations for whether or not to play the bets, how to play them, as well as configurations for the basic strategy to use in playing the hands.  Simulations can then be run over a large number of hands to compare the results.

## The Results

All simulations below were run for 10 million hands each with the players playing perfect strategy.  Bet per hand was $15 but the simulation allows the player to have a negative balance.  

#### House Edge - Overall

The overall house edge based on regular play plus bonus bets, if any.

#### House Edge - 21+3 / Bust

The house edge for the bonus bet itself.

|                                          | Main Bet | Bonus Bet     | House Edge - Overall | House Edge - 21+3 | House Edge - Bust |
|------------------------------------------|----------|---------------|----------------------|-------------------|-------------------|
| Sim #1 - No Bonuses                      | $15      |               | 0.60%                |                   |                   |
| Sim #2 - 21+3 Bonus - Always             | $15      | $1            | 1.47%                | 13.30%            |                   |
| Sim #3 - Bust Bonus - Always             | $15      | $5            | 3.10%                |                   | 8.13%             |
| Sim #4 - Bust Bonus - 2-6                | $15      | $5            | 1.65%                |                   | 8.08%             |
| Sim #5 - Bust Bonus - 2-6+A              | $15      | $5            | 1.80%                |                   | 8.20%             |
| Sim #6 - Bust Bonus - Only 6             | $15      | $5            | 0.87%                |                   | 8.15%             |
| Sim #7 - Bust Bonus - Only A             | $15      | $5            | 0.80%                |                   | 8.94%             |
| Sim #8 - Bust Bonus - Always, heavy on 6 | $15      | $5 ($15 on 6) | 3.54%                |                   | 8.19%             |

#### Rules in play:
* 6 decks
* 3 players (# of players should have no effect)
* Dealer hits on soft 17
* Blackjack pays 3:2
* Player can split aces
* Player can split up to 4 hands 

**Simulation #1 -** This is the control.  No bonuses played.

**Simulation #2 -** 21+3 bonus was played on every hand.

**Simulation #3 -** Bust bonus was played on every hand.

**Simulation #4 -** Bust bonus was played when a dealer showed a 2 through 6.

**Simulation #5 -** Bust bonus was played when a dealer showed a 2 through 6 or an ace.

**Simulation #6 -** Bust bonus was only played when the dealer showed a 6.

**Simulation #7 -** Bust bonus was only played when the dealer showed an ace.

**Simulation #8 -** Bust bonus was played on every hand and the bet was higher when the dealer showed a 6.

## Interpreting the Results

As you can see, the house edge on the bonus bets is pretty terrible for the player.  About 13% for the 21+3 bonus and about 8% for the bust bonus with little variation based on how it's played.  The effect on the overall house edge depends on how often the bonus bet is played and the amount of the bet.  Strategies where the bonus bet is played less frequently (e.g., only playing the bust bonus on 6 or A) are less detrimental to the player overall.

## So... Should I Play The Bonuses?

If you have fun playing the bonuses and don't mind losing more money, then sure.  But from a mathematical perspective?  Absolutely not.