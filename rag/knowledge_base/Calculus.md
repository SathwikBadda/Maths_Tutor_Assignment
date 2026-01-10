# Formulas

## Limits (Evaluation and Standard Forms)

Fundamental Identity: limit as x -> a of [x^n - a^n] / [x - a] = n * a^(n-1)

Trigonometric Limits (x -> 0):

(sin x) / x = 1

(tan x) / x = 1

(sin^-1 x) / x = 1 

(tan^-1 x) / x = 1 

(1 - cos x) / x^2 = 1/2

Exponential and Logarithmic (x -> 0):

(e^x - 1) / x = 1

(a^x - 1) / x = ln(a)

log(1 + x) / x = 1 

Euler's Form (Exponential):

limit as x -> infinity of (1 + 1/x)^x = e

limit as x -> 0 of (1 + x)^(1/x) = e 

limit as x -> a of [f(x)]^g(x) = exp[limit as x -> a of g(x) * (f(x) - 1)] when f(x) -> 1 and g(x) -> infinity

## Derivatives (Standard Functions and Rules)

Basic Rules:

Power Rule: d/dx (x^n) = n * x^(n-1)

Product Rule: d/dx (u * v) = u'v + uv'

Quotient Rule: d/dx (u / v) = (u'v - uv') / v^2

Chain Rule: d/dx [f(g(x))] = f'(g(x)) * g'(x)

Trigonometric Derivatives:

d/dx (sin x) = cos x

d/dx (cos x) = -sin x

d/dx (tan x) = sec^2 x

d/dx (cot x) = -csc^2 x

d/dx (sec x) = sec x * tan x

d/dx (csc x) = -csc x * cot x

Inverse Trigonometric Derivatives:

d/dx (sin^-1 x) = 1 / sqrt(1 - x^2)

d/dx (cos^-1 x) = -1 / sqrt(1 - x^2)

d/dx (tan^-1 x) = 1 / (1 + x^2)

Exponential and Logarithmic:

d/dx (e^x) = e^x

d/dx (a^x) = a^x * ln(a)

d/dx (ln x) = 1 / x

## Integration (Indefinite and Standard Forms)

Basic Integrals:

Int x^n dx = [x^(n+1) / (n+1)] + C (n!= -1)

Int (1/x) dx = ln|x| + C

Int e^x dx = e^x + C

Int a^x dx = [a^x / ln a] + C

Trigonometric Integrals:

Int sin x dx = -cos x + C

Int cos x dx = sin x + C

Int sec^2 x dx = tan x + C

Int csc^2 x dx = -cot x + C

Int tan x dx = ln|sec x| + C

Int cot x dx = ln|sin x| + C

Int sec x dx = ln|sec x + tan x| + C

Special Rational Forms:

Int 1 / (x^2 + a^2) dx = (1/a) * tan^-1(x/a) + C

Int 1 / sqrt(a^2 - x^2) dx = sin^-1(x/a) + C

Int 1 / (x^2 - a^2) dx = [1 / 2a] * ln|(x - a) / (x + a)| + C

Int 1 / (a^2 - x^2) dx = [1 / 2a] * ln|(a + x) / (a - x)| + C

Integration by Parts: Int u * dv = uv - Int v * du

## Definite Integration Properties

Fundamental Theorem: Int from a to b of f'(x) dx = f(b) - f(a)

King Property: Int from 0 to a of f(x) dx = Int from 0 to a of f(a-x) dx

Additivity Property: Int from a to b of f(x) dx = Int from a to c of f(x) dx + Int from c to b of f(x) dx

Odd/Even Property (Int from -a to a):

If f(-x) = f(x) [Even]: Result = 2 * Int from 0 to a of f(x) dx

If f(-x) = -f(x) [Odd]: Result = 0

Periodic Property: If f(x + T) = f(x), then Int from 0 to nT of f(x) dx = n * Int from 0 to T of f(x) dx

## Applications of Derivatives (AOD)

Tangent Equation: (y - y1) = f'(x1) * (x - x1)

Normal Equation: (y - y1) = [-1 / f'(x1)] * (x - x1)

Approximations: f(x + delta_x) approximately equals f(x) + f'(x) * delta_x

Lengths in AOD:

Length of Tangent = |y1 * sqrt(1 + (1/m^2))|

Length of Normal = |y1 * sqrt(1 + m^2)|

Length of Subtangent = |y1 / m|

Length of Subnormal = |y1 * m|

## Differential Equations

First Order Linear DE: dy/dx + P(x)y = Q(x)

Integrating Factor (IF) = exp(Int P(x) dx)

General Solution: y * (IF) = Int [Q(x) * (IF)] dx + C

Variable Separable: f(x) dx = g(y) dy

Homogeneous DE: dy/dx = f(y/x). Use substitution y = vx


# Theorems

## Rolle's Theorem

Definition: Let f(x) be a function that satisfies three conditions:

It is continuous on the closed interval [a, b].

It is differentiable on the open interval (a, b).

The function values at the endpoints are equal, i.e., f(a) = f(b). Result: There exists at least one point 'c' in the interval (a, b) such that f'(c) = 0.

Explanation: If a smooth curve starts and ends at the same height, it must have at least one "peak" or "valley" where the tangent is perfectly horizontal. 

JEE Example: Verify Rolle's Theorem for f(x) = x^2 - 4x + 3 in the interval.

Step-by-Step Application:

Step 1: Check continuity. f(x) is a polynomial, so it is continuous on.

Step 2: Check differentiability. f'(x) = 2x - 4, which exists for all x in (1, 3).

Step 3: Check endpoints. f(1) = 1 - 4 + 3 = 0; f(3) = 9 - 12 + 3 = 0. Since f(1) = f(3), the condition is met.

Step 4: Find 'c'. Set f'(c) = 0 => 2c - 4 = 0 => c = 2.

Step 5: Verify result. c = 2 lies within the interval (1, 3). Theorem verified.

## Lagrange's Mean Value Theorem (LMVT)

Definition: Let f(x) be continuous on [a, b] and differentiable on (a, b). Result: There exists at least one point 'c' in (a, b) such that f'(c) = [f(b) - f(a)] / (b - a).

Explanation: The instantaneous rate of change (tangent slope) at some point is equal to the average rate of change (secant slope) over the whole interval. 

Real-World Application: Speeding Tickets. If a car travels 100 miles in 2 hours, its average speed is 50 mph. LMVT proves that the car's speedometer must have read exactly 50 mph at least once during the trip.

Step-by-Step Application:

Step 1: Verify f(x) is continuous and differentiable on the given interval.

Step 2: Calculate the average slope: m = [f(b) - f(a)] / (b - a).

Step 3: Differentiate the function to get f'(x).

Step 4: Solve the equation f'(c) = m for 'c'.

## Newton-Leibniz Theorem (Differentiation Under Integral Sign)

Definition: Used to find the derivative of a definite integral where the limits are functions of x. Formula: d/dx [integral from h(x) to g(x) of f(t) dt] = f(g(x)) * g'(x) - f(h(x)) * h'(x).

Explanation: To differentiate an integral, you plug the upper limit into the function and multiply by its derivative, then subtract the lower limit plugged into the function multiplied by its derivative. 

JEE Example: Find the derivative of F(x) = integral from 0 to x^2 of cos(t) dt. 

Step-by-Step Application:

Step 1: Identify upper limit g(x) = x^2 and lower limit h(x) = 0.

Step 2: Plug upper limit into the function: cos(x^2).

Step 3: Multiply by derivative of upper limit: cos(x^2) * (2x).

Step 4: Plug lower limit into function: cos(0) = 1.

Step 5: Multiply by derivative of lower limit: 1 * (0) = 0.

Step 6: Result: 2x * cos(x^2).

## L'Hôpital's Rule

Definition: For functions f(x) and g(x), if the limit as x approaches 'a' of f(x)/g(x) results in an indeterminate form (0/0 or infinity/infinity). Result: limit as x -> a of f(x)/g(x) = limit as x -> a of f'(x)/g'(x).

Explanation: You can resolve "impossible" limits by differentiating the numerator and denominator separately until the result is defined. 

Step-by-Step Application:

Step 1: Perform direct substitution to confirm the form is 0/0 or inf/inf. 

Step 2: Differentiate numerator f(x) to get f'(x).

Step 3: Differentiate denominator g(x) to get g'(x).

Step 4: Re-evaluate the limit. If it's still 0/0, repeat the steps.

## Intermediate Value Theorem (IVT)

Definition: If f(x) is continuous on [a, b] and K is any number between f(a) and f(b), then there exists at least one number 'c' in (a, b) such that f(c) = K. 

Explanation: A continuous function cannot "jump" over values. To get from height A to height B, it must pass through every height in between. 

JEE Application: Used to prove that an equation f(x) = 0 has at least one real root in an interval [a, b] if f(a) and f(b) have opposite signs (one is positive, one is negative). 

## Sandwich Theorem (Squeeze Theorem)

Definition: If g(x) <= f(x) <= h(x) for all x near 'a', and the limits of g(x) and h(x) as x approaches 'a' are both equal to L. Result: The limit of f(x) as x approaches 'a' must also be L. 

Explanation: If a function is "trapped" between two other functions that are both heading to the same point, the middle function is forced to that point as well. 

JEE Example: Evaluate limit as x -> infinity of (sin x) / x.

Step-by-Step Application:

Step 1: Identify bounds. We know -1 <= sin x <= 1.

Step 2: Divide by x: -1/x <= (sin x) / x <= 1/x.

Step 3: Take limits. limit as x -> infinity of -1/x = 0; limit of 1/x = 0.

Step 4: Result: Since both outer limits are 0, the middle limit must be 0.

## Fundamental Theorem of Calculus (FTC)

Part 1 (Area Function): If f is continuous on [a, b], then the function G(x) = integral from 'a' to 'x' of f(t) dt is an antiderivative of f.

Part 2 (Evaluation): Integral from a to b of f(x) dx = F(b) - F(a), where F is any antiderivative of f. 

Explanation: This theorem bridges the gap between differentiation and integration, proving they are inverse operations. 

Real-World Application: Engineering/Physics. Finding total work done by a variable force over a distance by calculating the area under the force-displacement graph.


# Solution Template 

## Pattern  Limits - Series Expansion for Complex Forms

Question: Evaluate the limit as x approaches 0 of: [sin(x^2) - x^2] / x^6

solun: Step 1: Identify the indeterminate form by substituting x = 0. The result is 0/0.

solun: Step 2: Use the standard series expansion for sin(y) = y - (y^3 / 3!) + (y^5 / 5!) -...

solun: Step 3: Substitute y = x^2 into the expansion: sin(x^2) = x^2 - (x^6 / 6) + (x^10 / 120) -...

solun: Step 4: Substitute this expansion back into the original limit expression: [(x^2 - x^6/6 + x^10/120 -...) - x^2] / x^6

solun: Step 5: Simplify the numerator by cancelling x^2: [-x^6/6 + x^10/120 -...] / x^6

solun: Step 6: Divide each term by x^6: -1/6 + x^4/120 -...

solun: Step 7: Apply the limit x -> 0. All terms with x become zero. The final result is -1/6.

## Pattern  Optimization - Absolute Extrema in a Closed Interval

Question: Find the absolute maximum and minimum values of the function f(x) = 3*sqrt(x-2) + sqrt(4-x) in its domain.

solun: Step 1: Determine the domain. For square roots to be real, x-2 >= 0 and 4-x >= 0. This gives the interval [1, 2].

solun: Step 2: Find the first derivative f'(x) to locate critical points.

solun: Step 3: f'(x) = 3/[2*sqrt(x-2)] - 1/[2*sqrt(4-x)].

solun: Step 4: Set f'(x) = 0 to solve for x: 3/sqrt(x-2) = 1/sqrt(4-x).

solun: Step 5: Cross-multiply and square both sides: 9*(4 - x) = x - 2 => 36 - 9x = x - 2.

solun: Step 6: Solve for x: 10x = 38 => x = 3.8.

solun: Step 7: Evaluate the function at the endpoints and the critical point:

f(2) = 3*sqrt(0) + sqrt(2) = 1.414

f(4) = 3*sqrt(2) + sqrt(0) = 4.242

f(3.8) = 3*sqrt(1.8) + sqrt(0.2) = sqrt(20) = 4.472

solun: Step 8: Compare values. Absolute Maximum is sqrt(20) and Absolute Minimum is sqrt(2).

## Pattern Differentiability - Inverse Trig Substitution

Question: If y = sin^-1[ (2x) / (1 + x^2) ], find the value of dy/dx for the range |x| < 1.

solun: Step 1: Use a trigonometric substitution to simplify the expression. Let x = tan(theta).

solun: Step 2: Recall the identity sin(2*theta) = (2*tan(theta)) / (1 + tan^2(theta)).

solun: Step 3: Substitute this into y: y = sin^-1[ sin(2*theta) ].

solun: Step 4: Since |x| < 1, theta is in the range where sin^-1(sin) cancels out. So, y = 2*theta.

solun: Step 5: Convert back to x using theta = tan^-1(x). Thus, y = 2 * tan^-1(x).

solun: Step 6: Differentiate with respect to x: dy/dx = 2 * [1 / (1 + x^2)].

solun: Step 7: The final result is 2 / (1 + x^2).

## Pattern  AOD - Tangent at Point of Maximum Slope

Question: Find the equation of the tangent to the curve y = x^3 - 3x + 2 at the point where the slope is maximum.

solun: Step 1: Define the slope function m = dy/dx = 3x^2 - 3.

solun: Step 2: To maximize the slope, find the derivative of the slope: dm/dx = 6x.

solun: Step 3: Set dm/dx = 0 to find the inflection point: 6x = 0 => x = 0.

solun: Step 4: Verify it is a maximum/minimum. Since d^2m/dx^2 = 6, this point is actually where slope is minimum for the whole curve, but in JEE, this pattern usually asks for the point of inflection. Let's find the point: At x = 0, y = 0^3 - 3(0) + 2 = 2.

solun: Step 5: Calculate the slope at x = 0: m = 3(0)^2 - 3 = -3.

solun: Step 6: Use point-slope form: y - 2 = -3 * (x - 0).

solun: Step 7: Simplify the equation: y + 3x = 2.

## Pattern  Limits - Forms of 1 to the power of Infinity

Question: Evaluate the limit as x approaches 0 of: [ (1 + 5x^2) / (1 + 3x^2) ] ^ (1/x^2)

solun: Step 1: Identify the form. As x -> 0, the base approaches 1 and the exponent approaches infinity. This is the 1^inf form.

solun: Step 2: Apply the standard rule: limit [f(x)]^g(x) = exp( limit g(x) * [f(x) - 1] ).

solun: Step 3: Set f(x) = (1 + 5x^2)/(1 + 3x^2) and g(x) = 1/x^2.

solun: Step 4: Calculate f(x) - 1: [(1 + 5x^2) - (1 + 3x^2)] / (1 + 3x^2) = (2x^2) / (1 + 3x^2).

solun: Step 5: Multiply by g(x): (1/x^2) * [(2x^2) / (1 + 3x^2)] = 2 / (1 + 3x^2).

solun: Step 6: Take the limit as x -> 0: 2 / (1 + 0) = 2.

solun: Step 7: Final result is e^2.

## Pattern  Definite Integration - The King Property

Question: Evaluate the integral from 0 to pi/2 of: [sin^3(x)] / [sin^3(x) + cos^3(x)] dx

solun: Step 1: Let the given integral be I.

solun: Step 2: Apply the King Property: integral from 0 to a of f(x) = integral from 0 to a of f(a - x).

solun: Step 3: Replace x with pi/2 - x. Since sin(pi/2 - x) = cos(x) and vice versa, the new integral is: I = integral from 0 to pi/2 of [cos^3(x)] / [cos^3(x) + sin^3(x)] dx.

solun: Step 4: Add the two versions of I: 2I = integral from 0 to pi/2 of [sin^3(x) + cos^3(x)] / [sin^3(x) + cos^3(x)] dx.

solun: Step 5: The integrand simplifies to 1: 2I = integral from 0 to pi/2 of 1 dx.

solun: Step 6: Evaluate: 2I = [x] from 0 to pi/2 = pi/2.

solun: Step 7: Final result: I = pi/4.

## Pattern Area Under Curves - Splitting with Modulus

Question: Find the area enclosed between the curves y = x*|x| and y = x - |x|.

solun: Step 1: Split the functions based on the sign of x.

solun: Step 2: Case x >= 0: y = x^2 and y = x - x = 0. The curves meet only at x = 0.

solun: Step 3: Case x < 0: y = -x^2 and y = x - (-x) = 2x.

solun: Step 4: Find intersection points for x < 0: -x^2 = 2x => x^2 + 2x = 0 => x = -2.

solun: Step 5: Set up the integral for the area in the negative region: Integral from -2 to 0 of [upper curve - lower curve].

solun: Step 6: In the interval [-2, 0], -x^2 is higher than 2x. Integral: Integral from -2 to 0 of (-x^2 - 2x) dx.

solun: Step 7: Evaluate: [-x^3/3 - x^2] from -2 to 0 = (0) - (-(-8)/3 - 4) = -(8/3 - 4) = 4/3.

solun: Step 8: Final area is 4/3 square units.

## Pattern Inflection Points - Concavity and Sign Change

Question: Find the point(s) of inflection for the function f(x) = x^3 - 6x^2 + 12.

solun: Step 1: Find the first derivative: f'(x) = 3x^2 - 12x.

solun: Step 2: Find the second derivative: f''(x) = 6x - 12.

solun: Step 3: Set the second derivative to zero: 6x - 12 = 0 => x = 2.

solun: Step 4: Check for a sign change in f''(x) around x = 2.

solun: Step 5: For x < 2, f''(x) is negative (concave down). For x > 2, f''(x) is positive (concave up).

solun: Step 6: Since the concavity changes, x = 2 is an inflection point.

solun: Step 7: Calculate the y-coordinate: f(2) = 2^3 - 6(2^2) + 12 = 8 - 24 + 12 = -4. Result: (2, -4).

## Pattern  Differential Equations - Integrating Factor Method

Question: Solve the differential equation: dy/dx + y * [2x / (x^2 + 4)] = 1 / (x^2 + 4)^2

solun: Step 1: Identify the form. It is a first-order linear DE: dy/dx + P(x)y = Q(x).

solun: Step 2: Identify P(x) = 2x / (x^2 + 4).

solun: Step 3: Calculate the Integrating Factor (IF): IF = exp( integral P(x) dx ).

solun: Step 4: integral [2x / (x^2 + 4)] dx = ln(x^2 + 4). Thus, IF = exp(ln(x^2 + 4)) = x^2 + 4.

solun: Step 5: The solution is y * (IF) = integral [Q(x) * (IF)] dx.

solun: Step 6: y * (x^2 + 4) = integral [ (1 / (x^2 + 4)^2) * (x^2 + 4) ] dx = integral [ 1 / (x^2 + 4) ] dx.

solun: Step 7: Evaluate the integral: (1/2) * tan^-1(x/2) + C.

solun: Step 8: Final solution: y = [(1/2) * tan^-1(x/2) + C] / (x^2 + 4).

## Pattern  Differentiability - Critical Points of Power Functions

Question: Find the number of critical points of the function f(x) = (x - 2)^(2/3) * (2x + 1).

solun: Step 1: Apply the product rule to find f'(x).

solun: Step 2: f'(x) = (2/3)*(x - 2)^(-1/3)*(2x + 1) + (x - 2)^(2/3)*(2).

solun: Step 3: Take a common factor: [2 / (3*(x-2)^(1/3))] * [(2x + 1) + 3*(x - 2)].

solun: Step 4: Simplify the numerator: (2x + 1 + 3x - 6) = 5x - 5.

solun: Step 5: So, f'(x) = [2 * (5x - 5)] / [3 * (x - 2)^(1/3)].

solun: Step 6: Critical points occur where f'(x) = 0 or is undefined.

solun: Step 7: f'(x) = 0 at x = 1. f'(x) is undefined at x = 2.

solun: Step 8: Total number of critical points is 2.