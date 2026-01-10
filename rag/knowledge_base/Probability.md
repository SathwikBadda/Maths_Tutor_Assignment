# Formulas

## Fundamental Axioms and Basic Rules

Classical Definition: P(A) = (Number of favorable outcomes) / (Total number of possible outcomes) 

Range of Probability: 0 <= P(A) <= 1 

Certain Event: P(S) = 1 (where S is the sample space) 

Impossible Event: P(null set) = 0 

Complementary Event: P(not A) = 1 - P(A) 

## Addition Formulas (Union of Events)

General Addition Rule: P(A or B) = P(A) + P(B) - P(A and B) 

Mutually Exclusive Events: P(A or B) = P(A) + P(B) 

Exhaustive Events: P(A or B or C...) = 1 (if events cover the entire sample space) 

De Morgan's Laws (Set Mapping):

P(not (A or B)) = P((not A) and (not B))

P(not (A and B)) = P((not A) or (not B))

## Conditional and Multiplication Formulas

Conditional Probability: P(A given B) = P(A and B) / P(B) 

General Multiplication Rule: P(A and B) = P(A) * P(B given A) 

Independent Events: P(A and B) = P(A) * P(B) 

Independent Outcome of At Least One Event: P(A or B) = 1 - P(not A) * P(not B) 

## Formulas for Three Events (A, B, C)

Union of Three Events: P(A or B or C) = P(A) + P(B) + P(C) - P(A and B) - P(B and C) - P(A and C) + P(A and B and C)

At Least Two Occur: P(A and B) + P(B and C) + P(C and A) - 2 * P(A and B and C) 

Exactly Two Occur: P(A and B) + P(B and C) + P(C and A) - 3 * P(A and B and C) 

Exactly One Occurs: P(A) + P(B) + P(C) - 2 * + 3 * P(A and B and C) 

## Binomial Distribution (Bernoulli Trials)

Used for repeated trials with two outcomes (Success/Failure) and constant probability 'p'. 

Probability Mass Function (PMF): P(X = r) = nCr * p^r * q^(n-r) 

n = total number of trials

r = number of required successes

p = probability of success in one trial

q = probability of failure (1 - p)

Mean (mu): n * p 

Variance (Var): n * p * q 

Standard Deviation (sigma): sqrt(n * p * q) 

Sum of Successes Inequality: P(X >= r) = sum from k=r to n of [nCk * p^k * q^(n-k)]

Probability of At Least One Success: 1 - q^n

## Random Variable and Discrete Distributions

Expected Value (Mean): E(X) = sum of [xi * P(xi)]

Mean of X squared: E(X^2) = sum of [xi^2 * P(xi)]

Variance of X: Var(X) = E(X^2) - [E(X)]^2 

## Geometrical and Statistical Relationships

Geometrical Probability: P = (Area of favorable region) / (Area of total sample region)

Total Probability formula: P(A) = sum of [P(A given Ei) * P(Ei)]

Inverse Cause formula (Numerator for Bayes): P(Ei given A) = [P(A given Ei) * P(Ei)] / (Total Probability) 

## Multi-Draw Dynamics (With vs. Without Replacement)

With Replacement: P(draw 1 and draw 2) = P(draw 1) * P(draw 1) (trials are independent)

Without Replacement: P(draw 1 and draw 2) = P(draw 1) * P(draw 2 after draw 1) (trials are dependent; denominator decreases by 1)

# Theorems

## Addition Theorem of Probability

Definition: For any two events A and B in a sample space, the probability of either A or B (or both) occurring is the sum of their individual probabilities minus the probability of their intersection.

Formula: P(A or B) = P(A) + P(B) - P(A and B).

JEE Math Example: If P(A) = 0.6, P(B) = 0.3, and P(A and B) = 0.2, find P(A or B).

Real-World Example: Network Reliability. In a computer network with two servers, let A be the event "Server 1 is active" and B be "Server 2 is active." Engineers use this theorem to calculate the probability that the system is functional (at least one server is up).

Step-by-Step Solver Logic:

Step 1: Identify the probabilities of individual events P(A) and P(B).

Step 2: Identify the overlap P(A and B). If the events are "mutually exclusive," P(A and B) = 0.

Step 3: Substitute the values into the formula: P(A) + P(B) - P(A and B).

Step 4: Result: 0.6 + 0.3 - 0.2 = 0.7.

## Multiplication Theorem of Probability

Definition: The probability of two events A and B occurring together is the probability of the first event multiplied by the conditional probability of the second event occurring given the first has already happened.

Formula: P(A and B) = P(A) * P(B given A). (For independent events: P(A and B) = P(A) * P(B)).

JEE Math Example: A bag has 3 red and 2 black balls. If one ball is drawn and found red, what is the probability that a second drawn ball (without replacement) is black?

Real-World Example: Manufacturing Quality Control. If a product must pass two independent tests (e.g., durability and safety) to be shipped, the probability it is approved is the product of the probabilities of passing each test.

Step-by-Step Solver Logic:

Step 1: Calculate P(A), the probability of the first event. (e.g., P(Red) = 3/5).

Step 2: Update the sample space. After drawing one ball, total balls = 4.

Step 3: Calculate P(B given A). (e.g., P(Black after Red) = 2/4 = 1/2).

Step 4: Multiply the results: (3/5) * (1/2) = 3/10.

## Law of Total Probability

Definition: If the sample space is partitioned into several mutually exclusive and exhaustive events (causes) E1, E2...En, then the probability of any event A occurring is the weighted sum of the conditional probabilities of A given each cause.

Formula: P(A) = [P(A given E1) * P(E1)] + [P(A given E2) * P(E2)] +...

JEE Math Example: Bag 1 has 3 red, 4 black balls. Bag 2 has 5 red, 2 black balls. A bag is chosen at random and a ball is drawn. Find the probability it is red.

Real-World Example: Epidemiology. To find the total probability of a symptom occurring in a population, researchers sum the probability of that symptom given various diseases, weighted by the prevalence of each disease.

Step-by-Step Solver Logic:

Step 1: Identify the partitions (causes). Here, E1 = Bag 1, E2 = Bag 2. P(E1) = P(E2) = 1/2.

Step 2: Find the conditional probability of the outcome for each cause. P(Red given E1) = 3/7; P(Red given E2) = 5/7.

Step 3: Apply the formula: (1/2 * 3/7) + (1/2 * 5/7).

Step 4: Result: 3/14 + 5/14 = 8/14 = 4/7.

## Bayes' Theorem

Definition: Relates the conditional and marginal probabilities of random variables. It describes the probability of an event based on prior knowledge of conditions that might be related to the event.

Formula: P(Ei given A) = [P(A given Ei) * P(Ei)] / P(A).

JEE Math Example: A truth-teller (accuracy 3/4) rolls a die and says it is a 5. What is the probability it is actually a 5?

Real-World Example: Email Spam Filters. If an email contains the word "Free," Bayes' Theorem calculates the probability the email is spam based on how often "Free" appears in known spam emails versus legitimate ones.

Step-by-Step Solver Logic:

Step 1: Define the prior probabilities. P(Actually 5) = 1/6; P(Not 5) = 5/6.

Step 2: Define likelihoods. P(Says 5 given it is 5) = 3/4. P(Says 5 given it is not 5) = 1/4 * 1/5 = 1/20 (lied and chose 5 specifically).

Step 3: Calculate Total Probability P(Says 5) using the Law of Total Probability: (1/6 * 3/4) + (5/6 * 1/20) = 1/6.

Step 4: Apply Bayes' Formula: [(1/6 * 3/4) / (1/6)].

Step 5: Result: 3/4.

## Bernoulli Trials and Binomial Distribution

Definition: A sequence of independent experiments where each trial has exactly two outcomes (Success/Failure) and the probability of success 'p' is constant.

Formula: P(X = r) = nCr * p^r * q^(n-r).

JEE Math Example: A fair coin is tossed 10 times. Find the probability of getting exactly 7 heads.

Real-World Example: Pharmaceutical Testing. If a vaccine has a 90% success rate, researchers use this theorem to predict the probability that exactly 95 out of 100 people in a clinical trial will develop immunity.

Step-by-Step Solver Logic:

Step 1: Confirm if trials are independent and outcomes are binary. (Yes: Coin toss).

Step 2: Identify n = 10, r = 7, p = 0.5, q = 0.5.

Step 3: Apply the formula: (10C7) * (0.5)^7 * (0.5)^3.

Step 4: Result: 120 * (0.5)^10 = 120 / 1024 = 15/128.


# Solution Template

## Pattern  Bayes' Theorem (Diagnosis and Conditional Likelihood)

Question: A doctor knows that 90 percent of sick children in a neighborhood have the flu (F), while 10 percent have measles (M). A rash (R) is a symptom of measles with a probability of 0.95. However, 8 percent of children with flu also develop a rash. If a child is found to have a rash, find the probability that the child has measles. 

Solution:

Step 1 (Identify Priors): P(F) = 0.9 (Flu) and P(M) = 0.1 (Measles).

Step 2 (Identify Likelihoods): P(R given M) = 0.95 and P(R given F) = 0.08.

Step 3 (Calculate Total Probability of Rash): P(R) = + P(R) = (0.95 * 0.1) + (0.08 * 0.9) = 0.095 + 0.072 = 0.167.

Step 4 (Apply Bayes' Theorem): P(M given R) = / P(R).

Step 5 (Final Calculation): 0.095 / 0.167 = 95 / 167.

## Pattern  Geometrical Probability (Area and Coordinate Boundaries)

Question: Two random real numbers x and y in the range are chosen. Let A be the event that the absolute difference between them is less than or equal to 'a'. If P(A) = 11/36, find the value of 'a'.

Solution:

Step 1 (Analyze Sample Space): The total area of the region (square) is 60 * 60 = 3600.

Step 2 (Define Event Region): The event |x - y| <= a is the region between lines y = x + a and y = x - a.

Step 3 (Use Complementary Area): The area outside this region consists of two triangles with side length (60 - a).

Step 4 (Calculate Probabilities): P(A) = 1 -. 11/36 = 1 - [(60 - a)^2 / 3600].

Step 5 (Solve for a): (60 - a)^2 / 3600 = 1 - 11/36 = 25/36.

Step 6 (Simplify): (60 - a) / 60 = sqrt(25/36) = 5/6.

Step 7 (Final Result): 60 - a = 50 => a = 10.

## Pattern  Parity and Generating Functions (Sum of Outcomes)

Question: In a bag, there are three tickets numbered 1, 2, and 3. A ticket is drawn at random and put back, and this is done four times. Find the probability that the sum of the numbers is even. 

Solution:

Step 1 (Analyze Outcomes): Total outcomes n(S) = 3^4 = 81.

Step 2 (Define Parity): Probability of odd = 2/3 (tickets 1, 3); Probability of even = 1/3 (ticket 2).

Step 3 (Define Logic): The sum is even if the number of odd-numbered tickets drawn is 0, 2, or 4.

Step 4 (Use Generating Function/Parity Logic): The number of favorable ways is [P(1) + P(-1)] / 2, where P(x) = (x^1 + x^2 + x^3)^4.

Step 5 (Calculate): P(1) = (1+1+1)^4 = 81. P(-1) = (-1 + 1 - 1)^4 = (-1)^4 = 1.

Step 6 (Final Calculation): Favorable = (81 + 1) / 2 = 41.

Step 7 (Final Result): Prob = 41 / 81.

## Pattern Bayes' Theorem (Reliability and Truth-tellers)

Question: A man tells the truth 3 out of 4 times. He rolls a die and says it is a 5. Find the probability it is actually a 5.

Solution:

Step 1 (Define Causes): E1 = Actually a 5 (P = 1/6). E2 = Not a 5 (P = 5/6).

Step 2 (Identify Likelihoods): P(Says 5 given it is 5) = 3/4 (Truth).

Step 3 (Analyze the Lie): P(Says 5 given it is not 5) = (1/4) * (1/5) = 1/20 (Lied and specifically chose face 5 from the other 5 faces).

Step 4 (Calculate Total Prob of Saying 5): (1/6 * 3/4) + (5/6 * 1/20) = 1/8 + 1/24 = 4/24 = 1/6.

Step 5 (Apply Bayes' Theorem): Posterior Prob = (1/8) / (1/6) = 6/8.

Step 6 (Final Result): 3/4.

## Pattern  Binomial Distribution (Successive Trials with Constraints)

Question: A coin is tossed 'n' times. If the probability of getting 7 heads is equal to the probability of getting 9 heads, find 'n' and the probability of getting 3 heads. 

Solution:

Step 1 (Set Equality): nC7 * (1/2)^n = nC9 * (1/2)^n.

Step 2 (Simplify combinations): nC7 = nC9.

Step 3 (Apply nCr property): nCr = nC(n-r) => 7 = n - 9.

Step 4 (Identify n): n = 16.

Step 5 (Find specific probability): P(3 heads) = 16C3 * (1/2)^16.

Step 6 (Final Calculation): 560 / 65536 = 35 / 2^12. 

## Pattern  Variance of Discrete Random Variables

Question: A box contains 10 pens, of which 3 are defective. A sample of 2 pens is drawn at random. Let X denote the number of defective pens. Find the variance of X.

Solution:

Step 1 (Determine Probability Distribution): Total ways = 10C2 = 45. P(X=0) = 7C2 / 45 = 21/45. P(X=1) = (3C1 * 7C1) / 45 = 21/45. P(X=2) = 3C2 / 45 = 3/45.

Step 2 (Calculate Mean): E(X) = 0*(21/45) + 1*(21/45) + 2*(3/45) = 27/45 = 3/5.

Step 3 (Calculate Mean of Squares): E(X^2) = 0^2*(21/45) + 1^2*(21/45) + 2^2*(3/45) = 33/45 = 11/15.

Step 4 (Apply Variance Formula): Var = E(X^2) - [E(X)]^2.

Step 5 (Final Result): 11/15 - 9/25 = (55 - 27) / 75 = 28/75.

## Pattern Independent Events (Probability of Survival/Success)

Question: Three ships A, B, and C sail from England to India. The ratio of their arriving safely is 2:5, 3:7, and 6:11 respectively. Find the probability that all ships arrive safely. 

Solution:

Step 1 (Convert Ratios to Probabilities): P(A) = 2 / (2 + 5) = 2/7. P(B) = 3 / (3 + 7) = 3/10. P(C) = 6 / (6 + 11) = 6/17.

Step 2 (Apply Independence Rule): Since arrivals are independent, multiply the individual probabilities.

Step 3 (Calculate): (2/7) * (3/10) * (6/17).

Step 4 (Final Result): 36 / 1190 = 18 / 595.

## Pattern Binomial Distribution (At Least Successes)

Question: A bag contains 2 white and 4 black balls. A ball is drawn 5 times with replacement. Find the probability that at least 4 of the drawn balls are white. 

Solution:

Step 1 (Define parameters): Success p = 2/6 = 1/3; failure q = 2/3. n = 5.

Step 2 (Set Condition): At least 4 means P(X = 4) + P(X = 5).

Step 3 (Calculate P(4)): 5C4 * (1/3)^4 * (2/3) = 5 * (1/81) * (2/3) = 10 / 243.

Step 4 (Calculate P(5)): 5C5 * (1/3)^5 = 1 * (1/243) = 1 / 243.

Step 5 (Final Result): 10/243 + 1/243 = 11 / 243.

## Pattern Sum of Outcomes (Multi-Dice Rolls)

Question: Three fair dice are thrown simultaneously. What is the probability of obtaining a total sum of 17 or 18? 

Solution:

Step 1 (Analyze Sample Space): Total outcomes = 6 * 6 * 6 = 216.

Step 2 (Identify Favorable Cases for 18): Only (6, 6, 6) [1 way].

Step 3 (Identify Favorable Cases for 17): (6, 6, 5), (6, 5, 6), (5, 6, 6) [3 ways].

Step 4 (Total Favorable): 1 + 3 = 4.

Step 5 (Final Calculation): 4 / 216.

Step 6 (Final Result): 1 / 54.

## Pattern  Minimum Trials (Success Probability Threshold)

Question: If the probability of hitting a target in any shot is 1/3, find the minimum number of independent shots required so that the probability of hitting the target at least once is greater than 5/6. 

Solution:

Step 1 (Use Complementary Event): P(at least one hit) = 1 - P(all misses).

Step 2 (Define miss probability): q = 1 - 1/3 = 2/3.

Step 3 (Set up Inequality): 1 - (2/3)^n > 5/6.

Step 4 (Simplify): (2/3)^n < 1 - 5/6 = 1/6.

Step 5 (Test Integer n): n = 1: 0.66. n = 2: 0.44. n = 3: 0.29. n = 4: 0.19. n = 5: 0.13.

Step 6 (Identify Threshold): Since 0.13 is less than 1/6 (0.166), n = 5 is the minimum.

Step 7 (Final Result): 5 shots.