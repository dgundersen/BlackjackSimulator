# BlackjackSimulator
Designed to run simulations of many blackjack games, specifically including a bust bonus and 3 card bonus found in casinos in Black Hawk, CO.

![bj_bonuses](https://user-images.githubusercontent.com/13021132/159364862-15cc5e33-c5e5-4b38-b1af-24afd873a839.jpg)

### Bust Bonus

The player is allowed to make a side bet, after the cards are dealt, that pays out if the dealer busts.  The suited payouts require all of the dealer's cards to be of the same suit.

So, for example, the dealer has an up card of 6 and busts on 6 Q 9 non-suited then the bet pays even money.

If the dealer busts with a suited 8 8 8 then the bet pays 75:1.

### 3 Card Bonus

The side bet is placed before the deal.  After the cards are dealt, if your 2 cards and the dealer's up card make one of the hands listed then the bet pays out.  

For example, if you have a 6 7 and the dealer's up card is an 8 then the bet pays 10:1.

## So Should I Play The Bonuses?

My wife and I were discussing the merits of the bonuses and whether or not they make sense to play.  She plays the 3 card bonus while I generally avoid it.  We both play the bust bonus--usually on 2 through 6 and A--as it seems like it helps, but does it?

It's safe to assume that the casino would only offer these bonuses if they were in the house's favor.  So then the questions to be answered are:

1. What is the house's edge on these side bets?
2. Does it ever make sense for the player to play them?

## The Goal

I wrote this simulator to see just how good or bad these bets really are.  The simulator supports different configurations for whether or not to play the bets and exactly how to play them, as well as configurations for the basic strategy to use in playing the hands.  Simulations can then be run over thousands or millions of hands to compare the results.

## The Results

TBD

