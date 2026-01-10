# Formulas

## Basic Algebraic Identities

These are foundational for all expression manipulations and vertex identifications.

(a + b)^2 = a^2 + 2ab + b^2 

(a - b)^2 = a^2 - 2ab + b^2 

a^2 - b^2 = (a + b)(a - b) 

(a + b + c)^2 = a^2 + b^2 + c^2 + 2ab + 2bc + 2ca 

(a + b)^3 = a^3 + 3a^2b + 3ab^2 + b^3 

(a - b)^3 = a^3 - 3a^2b + 3ab^2 - b^3 

a^3 + b^3 = (a + b)(a^2 - ab + b^2) 

a^3 - b^3 = (a - b)(a^2 + ab + b^2) 

a^3 + b^3 + c^3 - 3abc = (a + b + c)(a^2 + b^2 + c^2 - ab - bc - ca) 

Special Case: If a + b + c = 0, then a^3 + b^3 + c^3 = 3abc. 

## Quadratic Equations (ax^2 + bx + c = 0)

The Solver Agent uses these for root extraction and vertex optimization.

Roots (Quadratic Formula): x = [-b +/- sqrt(b^2 - 4ac)] / (2a)

Discriminant (D): D = b^2 - 4ac

Nature of Roots:

D > 0: Real and distinct roots.

D = 0: Real and equal roots (repeated).

D < 0: Complex conjugate roots.

Vieta’s Relations:

Sum of roots (alpha + beta) = -b/a

Product of roots (alpha * beta) = c/a

Formation of Equation: x^2 - (sum of roots)x + (product of roots) = 0

Vertex of Parabola: (-b/2a, -D/4a)

## Location of Roots (Case-wise Constraints)

Crucial for the Verifier Agent to check edge cases and parameter ranges.

Case 1: Both roots greater than k: D >= 0, -b/2a > k, and f(k) > 0.

Case 2: Both roots less than k: D >= 0, -b/2a < k, and f(k) > 0.

Case 3: k lies between roots: f(k) < 0.

Case 4: Exactly one root in (k1, k2): f(k1) * f(k2) < 0.

Case 5: Both roots in (k1, k2): D >= 0, k1 < -b/2a < k2, f(k1) > 0, and f(k2) > 0.

## Complex Numbers (z = x + iy)

Modulus: |z| = sqrt(x^2 + y^2)

Conjugate: z_bar = x - iy

Argument: theta = tan^-1(y/x)

Euler's Form: z = r * e^(i * theta)

De Moivre’s Theorem: [cos(theta) + isin(theta)]^n = cos(ntheta) + isin(ntheta)

Cube Roots of Unity (x^3 = 1): Roots are 1, w, and w^2.

w = [-1 + i*sqrt(3)] / 2

w^2 = [-1 - i*sqrt(3)] / 2

Properties: 1 + w + w^2 = 0 and w^3 = 1.

## Sequences and Series

Arithmetic Progression (AP):

nth term (an) = a + (n-1)d 

Sum (Sn) = (n/2) * [2a + (n-1)d] or (n/2) * [first + last]

Geometric Progression (GP):

nth term (an) = a * r^(n-1) 

Sum (Sn) = a(r^n - 1) / (r - 1) for r!= 1 

Infinite Sum (S_inf) = a / (1 - r) for |r| < 1 

Arithmetic-Geometric Progression (AGP): Sum calculated by shifting series by 'r' and subtracting.

Means Relationship: AM >= GM >= HM

AM = (a + b) / 2

GM = sqrt(a * b)

HM = 2ab / (a + b)

## Binomial Theorem

General Expansion: (a + b)^n = nC0a^n + nC1a^(n-1)b +... + nCnb^n

General Term: T(r+1) = nCr * a^(n-r) * b^r

Middle Term:

If n is even: term at (n/2 + 1).

If n is odd: terms at (n+1)/2 and (n+3)/2.

Sum of Coefficients: Put a = b = 1; Sum = 2^n.

## Logarithms and Exponents

Log Rules:

log(ab) = log a + log b 

log(a/b) = log a - log b

log(a^n) = n * log a 

log_b (a) = (log_c a) / (log_c b)

Exponent Rules:

a^m * a^n = a^(m+n) 

a^m / a^n = a^(m-n) 

(a^m)^n = a^(mn) 

## Sets and Relations

Cardinality: n(A U B) = n(A) + n(B) - n(A intersection B) 

De Morgan's Laws: 

(A U B)' = A' intersection B'

(A intersection B)' = A' U B'

Types of Relations: 

Reflexive: (a, a) belongs to R for all a.

Symmetric: If (a, b) belongs to R, then (b, a) belongs to R.

Transitive: If (a, b) and (b, c) belong to R, then (a, c) belongs to R.

Equivalence: Relation is Reflexive + Symmetric + Transitive.


# Theorems

## Fundamental Theorem of Algebra

The Theorem: Every non-constant polynomial equation of degree 'n' has exactly 'n' complex roots (counting repeated roots).

Application Logic: Used by the Solver Agent to verify if all possible solutions of an equation (real + imaginary) have been found.

JEE Example: How many roots does x^4 + x^2 + 1 = 0 have?

Step 1: Identify the highest power (degree). Here n = 4.

Step 2: Apply the theorem. Since the degree is 4, there must be 4 roots in total.

Step 3: Solve to find 4 complex roots: +/- 0.5 + i * sqrt(3)/2 and +/- 0.5 - i * sqrt(3)/2.

Real World: Control Systems Engineering. Engineers use this to find the "poles" of a system. If the roots (poles) have positive real parts, the system (like an airplane autopilot) will be unstable and crash.

## Remainder Theorem

The Theorem: If a polynomial f(x) is divided by (x - a), the remainder is simply f(a).

Application Logic: Allows the Solver Agent to find remainders instantly without performing long division.

JEE Example: Find the remainder when x^3 - 2x^2 + 4 is divided by (x - 2).

Step 1: Identify the divisor (x - a). Here a = 2.

Step 2: Substitute a = 2 into the polynomial f(x).

Step 3: f(2) = (2)^3 - 2(2)^2 + 4 = 8 - 8 + 4 = 4.

Step 4: The remainder is 4.

Real World: Digital Signal Processing. Used in CRC (Cyclic Redundancy Check) to detect errors in data packets sent over the internet by checking if the remainder of a data polynomial is zero.

3. Factor Theorem

The Theorem: A linear expression (x - a) is a factor of polynomial f(x) if and only if f(a) = 0.

Application Logic: Primary tool for the Parser Agent to simplify high-degree equations into smaller, solvable parts.

JEE Example: Is (x - 1) a factor of x^3 - 6x^2 + 11x - 6?

Step 1: Set a = 1.

Step 2: Calculate f(1) = (1)^3 - 6(1)^2 + 11(1) - 6 = 1 - 6 + 11 - 6 = 0.

Step 3: Since f(1) = 0, (x - 1) is a confirmed factor.

Real World: Computer Graphics. Used to determine the points where a 3D curve (like the edge of a character) intersects a plane, allowing the computer to "clip" or hide parts of the image not visible to the user.

## Rational Root Theorem

The Theorem: For a polynomial with integer coefficients, any rational root p/q must have 'p' as a factor of the constant term and 'q' as a factor of the leading coefficient.

Application Logic: Used by the Solver Agent to generate a "list of suspects" (candidate roots) for equations that cannot be factored easily.

JEE Example: Find possible rational roots of 2x^3 + x - 3 = 0.

Step 1: Constant term is -3. Factors (p) = +/- 1, +/- 3.

Step 2: Leading coefficient is 2. Factors (q) = +/- 1, +/- 2.

Step 3: Possible roots (p/q) = +/- 1, +/- 3, +/- 1/2, +/- 3/2.

Step 4: Test suspects. f(1) = 2(1)^3 + 1 - 3 = 0. So x = 1 is a root.

Real World: Financial Modeling. Used to find the "Internal Rate of Return" (IRR) on an investment by solving the roots of a cash-flow polynomial.

## Vieta’s Formulas

The Theorem: Relates the sum and product of roots to the coefficients of the equation. For ax^2 + bx + c = 0, sum = -b/a and product = c/a.

Application Logic: Essential for solving "Symmetric Expressions" (like alpha^2 + beta^2) without knowing the actual values of the roots.

JEE Example: If alpha and beta are roots of x^2 - 5x + 6 = 0, find alpha^2 + beta^2.

Step 1: Sum (alpha + beta) = -(-5)/1 = 5.

Step 2: Product (alpha * beta) = 6/1 = 6.

Step 3: Use identity: alpha^2 + beta^2 = (alpha + beta)^2 - 2(alpha * beta).

Step 4: Substitute: (5)^2 - 2(6) = 25 - 12 = 13.

Real World: Ballistics/Physics. If a projectile reaches a height 'h' at times t1 and t2, Vieta's formulas are used to find the initial velocity and gravity relationship using the sum and product of those times.

## Binomial Theorem

The Theorem: Provides a formula for expanding (a + b)^n using combinations (nCr).

Application Logic: Used for finding specific coefficients or approximating large numbers (e.g., 1.01^10).

JEE Example: Find the 5th term in (x + 2y)^10.

Step 1: Use general term formula T(r+1) = nCr * a^(n-r) * b^r.

Step 2: For 5th term, set r = 4. n = 10, a = x, b = 2y.

Step 3: T_5 = 10C4 * x^(10-4) * (2y)^4.

Step 4: T_5 = 210 * x^6 * 16y^4 = 3360 * x^6 * y^4.

Real World: Probability and Statistics. Used in Binomial Distributions to calculate the odds of an event happening exactly 'k' times out of 'n' attempts (like flipping a coin or testing machine parts for defects).

## AM-GM Inequality Theorem

The Theorem: For positive numbers, the Arithmetic Mean (AM) is always greater than or equal to the Geometric Mean (GM).

Application Logic: The Verifier Agent uses this to set boundaries/ranges for variables. If a problem asks for "minimum value," this is the first logic gate.

JEE Example: Find the minimum value of 4^x + 4^(-x).

Step 1: Let a = 4^x and b = 4^(-x). Both are positive.

Step 2: Apply AM >= GM: (a + b) / 2 >= sqrt(a * b).

Step 3: (4^x + 4^-x) / 2 >= sqrt(4^x * 4^-x) = sqrt(4^0) = 1.

Step 4: 4^x + 4^-x >= 2. Min value is 2.

Real World: Logistics and Packaging. Used to minimize the surface area of a shipping container (cost) while keeping the volume (storage) constant.

## De Moivre’s Theorem

The Theorem: (cos theta + i * sin theta)^n = cos(n * theta) + i * sin(n * theta).

Application Logic: Drastically reduces the computational steps needed for high-power complex numbers.

JEE Example: Calculate (1 + i)^8.

Step 1: Convert (1 + i) to Polar Form: sqrt(2) * [cos(pi/4) + i * sin(pi/4)].

Step 2: Raise to power 8: (sqrt(2))^8 * [cos(8 * pi/4) + i * sin(8 * pi/4)].

Step 3: 16 * [cos(2pi) + i * sin(2pi)] = 16 * [1 + 0] = 16.

Real World: Electrical Engineering. Alternating Current (AC) circuits are modeled using complex numbers. This theorem allows engineers to calculate phase shifts and power consumption in complex grids.


# Solution Templates

## Pattern Binomial Theorem - Coefficients in Arithmetic Progression (AP)

Question: If the coefficients of x^4, x^5, and x^6 in the binomial expansion of (1 + x)^n are in A.P., find the maximum value of n.

Solution:

Step 1 (Identify Coefficients): The coefficients of x^r in (1 + x)^n is nCr. Therefore, the coefficients are nC4, nC5, and nC6.

Step 2 (Apply AP Condition): For three numbers a, b, c to be in AP, 2b = a + c. So, 2(nC5) = (nC4) + (nC6).

Step 3 (Expand Combinations): Use the formula nCr = n! / [r! * (n-r)!]. 2 * [n! / (5! * (n-5)!)] = [n! / (4! * (n-4)!)] + [n! / (6! * (n-6)!)]

Step 4 (Simplify Factorials): Divide the entire equation by n! and multiply by 6! * (n-4)! to clear denominators. 12 * (n-4) = 30 + (n-4) * (n-5)

Step 5 (Form Quadratic): Expand and rearrange: 12n - 48 = 30 + n^2 - 9n + 20 => n^2 - 21n + 98 = 0.

Step 6 (Solve for n): Factor the quadratic: (n - 7)(n - 14) = 0.

Step 7 (Final Result): n = 7 or n = 14. The maximum value of n is 14.

## Pattern Binomial Theorem - Remainder Problems

Question: Find the remainder when 428^2024 is divided by 21.

Solution:

Step 1 (Analyze the Base): Express the base 428 in terms of the divisor 21. 428 = (21 * 20) + 8.

Step 2 (Use Modular Logic): Since 428 is equivalent to 8 mod 21, the problem reduces to finding the remainder of 8^2024 divided by 21.

Step 3 (Simplify the Power): Write 8^2024 as (8^2)^1012 = 64^1012.

Step 4 (Analyze the New Base): Express 64 in terms of 21. 64 = (21 * 3) + 1.

Step 5 (Apply Power): (21 * 3 + 1)^1012 is equivalent to 1^1012 mod 21.

Step 6 (Final Result): 1^1012 = 1. The remainder is 1.

## Pattern  Quadratic Equations - Newton's Sums (Powers of Roots)

Question: Let alpha and beta be the roots of the equation x^2 - 6x - 2 = 0. If a_n = (alpha^n) - (beta^n) for n >= 1, find the value of (a_10 - 2a_8) / (2a_9).

Solution:

Step 1 (Recall Newton's Formula): For a quadratic ax^2 + bx + c = 0, the sums S_n satisfy: a*(S_n) + b*(S_n-1) + c*(S_n-2) = 0.

Step 2 (Apply to Given Equation): Here a = 1, b = -6, c = -2. So, 1*(a_10) - 6*(a_9) - 2*(a_8) = 0.

Step 3 (Rearrange the Terms): Group the terms required by the question: a_10 - 2a_8 = 6a_9.

Step 4 (Form the Ratio): Divide both sides by 2a_9 to match the target expression. (a_10 - 2a_8) / (2a_9) = (6a_9) / (2*a_9).

Step 5 (Final Result): The ratio simplifies to 3.

## Pattern  Complex Numbers - Geometry and Locus

Question: Find the locus of a complex number z if it satisfies the equation |z - 1| + |z + 1| = 4.

Solution:

Step 1 (Identify the Geometric Form): The equation |z - z1| + |z - z2| = K represents an ellipse if K > |z1 - z2|.

Step 2 (Identify Foci): Here z1 = 1 (1, 0) and z2 = -1 (-1, 0). The distance between them is 2.

Step 3 (Verify Condition): K = 4. Since 4 > 2, the locus is an ellipse.

Step 4 (Find Parameters): Sum of distances from foci = 2a = 4 => a = 2. Distance between foci = 2c = 2 => c = 1.

Step 5 (Calculate Minor Axis): Use b^2 = a^2 - c^2 = 2^2 - 1^2 = 3.

Step 6 (Construct Equation): The Cartesian equation is (x^2 / a^2) + (y^2 / b^2) = 1.

Step 7 (Final Result): The locus is the ellipse x^2/4 + y^2/3 = 1.

## Pattern  Sequences and Series - Arithmetic-Geometric Progression (AGP)

Question: Find the sum of the infinite series S = 1 + 2/3 + 3/3^2 + 4/3^3 +...

Solution:

Step 1 (Write the Series): S = 1 + 2/3 + 3/9 + 4/27 +...

Step 2 (Multiply by Ratio): Multiply the whole series by the common ratio r = 1/3. (1/3)*S = 1/3 + 2/9 + 3/27 +...

Step 3 (Subtract the Series): Subtract (1/3)S from S. S - (1/3)S = 1 + (2/3 - 1/3) + (3/9 - 2/9) + (4/27 - 3/27) +...

Step 4 (Simplify to GP): (2/3)S = 1 + 1/3 + 1/9 + 1/27 +...

Step 5 (Apply Infinite GP Formula): Sum of infinite GP = a / (1 - r) = 1 / (1 - 1/3) = 1 / (2/3) = 3/2.

Step 6 (Solve for S): (2/3)S = 3/2 => S = (3/2) * (3/2).

Step 7 (Final Result): S = 9/4.

## Pattern  Sequences and Series - Number of Common Terms in Two APs

Question: Find the number of common terms in two progressions: AP1 = 4, 9, 14,... (up to 25 terms) and AP2 = 3, 6, 9,... (up to 37 terms).

Solution:

Step 1 (Find Last Terms): L1 = 4 + (25 - 1)*5 = 124. L2 = 3 + (37 - 1)*3 = 111.

Step 2 (Identify Common Difference): Common difference of common terms D = LCM(d1, d2) = LCM(5, 3) = 15.

Step 3 (Find First Common Term): By inspection, the first common term is a = 9.

Step 4 (Set up Inequality): Common terms T_k must be less than or equal to the smaller of the two last terms (111). 9 + (k - 1)*15 <= 111.

Step 5 (Solve for k): 15*(k - 1) <= 102 => k - 1 <= 6.8.

Step 6 (Final Result): k = 7. There are 7 common terms.

## Pattern  Quadratic Equations - Higher Degree Symmetric Equations

Question: Find the number of real roots of the equation x^4 - 3x^3 + 4x^2 - 3x + 1 = 0.

Solution:

Step 1 (Observe Symmetry): The coefficients are symmetric (1, -3, 4, -3, 1). Divide the equation by x^2. (x^2 + 1/x^2) - 3(x + 1/x) + 4 = 0.

Step 2 (Substitute): Let y = x + 1/x. Then x^2 + 1/x^2 = y^2 - 2.

Step 3 (Transform Equation): (y^2 - 2) - 3y + 4 = 0 => y^2 - 3y + 2 = 0.

Step 4 (Solve for y): (y - 1)(y - 2) = 0. So y = 1 or y = 2.

Step 5 (Apply Constraint): For real x, |x + 1/x| must be >= 2.

Step 6 (Check y values): y = 1 is invalid (less than 2). y = 2 is valid (gives x = 1).

Step 7 (Final Result): There is only 1 real root (x = 1).

## Pattern  Complex Numbers - Evaluation using Quadratic Reduction

Question: If x = (3 - 5i) / 2, find the value of 2x^3 + 2x^2 - 7x + 72.

Solution:

Step 1 (Form a Quadratic): 2x = 3 - 5i => 2x - 3 = -5i.

Step 2 (Remove i): Square both sides: (2x - 3)^2 = (-5i)^2 => 4x^2 - 12x + 9 = -25.

Step 3 (Simplify Quadratic): 4x^2 - 12x + 34 = 0 => 2x^2 - 6x + 17 = 0.

Step 4 (Use Polynomial Division): Divide 2x^3 + 2x^2 - 7x + 72 by (2x^2 - 6x + 17).

Step 5 (Identify Remainder): The division gives a quotient and a remainder. 2x^3 + 2x^2 - 7x + 72 = (2x^2 - 6x + 17) * (x + 4) + 4.

Step 6 (Final Result): Since (2x^2 - 6x + 17) = 0, the entire value is 4.

## Pattern Sequences and Series - AM-GM Inequality for Optimization

Question: If a, b, c are positive real numbers such that a + b + c = 27, find the maximum value of a^2 * b^3 * c^4.

Solution:

Step 1 (Set up Groups): Divide a, b, c into groups matching their powers. Divide 'a' into 2 parts, 'b' into 3 parts, and 'c' into 4 parts.

Step 2 (Apply AM-GM): The parts are (a/2, a/2, b/3, b/3, b/3, c/4, c/4, c/4, c/4). There are 9 terms total.

Step 3 (Form the Mean): [2*(a/2) + 3*(b/3) + 4*(c/4)] / 9 >= [(a/2)^2 * (b/3)^3 * (c/4)^4]^(1/9).

Step 4 (Substitute sum): (a + b + c) / 9 >= [ (a^2 * b^3 * c^4) / (2^2 * 3^3 * 4^4) ]^(1/9).

Step 5 (Solve for product): 27 / 9 = 3. So, 3^9 >= (a^2 * b^3 * c^4) / (4 * 27 * 256).

Step 6 (Final Result): Max value = 3^9 * 2^2 * 3^3 * 2^8 = 3^12 * 2^10.

## Pattern Matrices - Infinitely Many Solutions (Consistency)

Question: Determine the values of lambda and mu for which the system x + y + z = 6, x + 2y + 3z = 10, x + 2y + lambda*z = mu has infinitely many solutions.

Solution:

Step 1 (Set Main Determinant to Zero): For infinite solutions, Det(A) = 0.

Step 2 (Calculate Det): | 1, 1, 1; 1, 2, 3; 1, 2, lambda | = 0.

Step 3 (Solve for lambda): 1*(2lambda - 6) - 1(lambda - 3) + 1*(2 - 2) = 0 => lambda - 3 = 0 => lambda = 3.

Step 4 (Check Sub-Determinants): For infinite solutions, Delta_x, Delta_y, Delta_z must also be 0.

Step 5 (Substitute lambda into Delta_x): | 6, 1, 1; 10, 2, 3; mu, 2, 3 | = 0.

Step 6 (Solve for mu): 6*(6 - 6) - 1*(30 - 3mu) + 1(20 - 2mu) = 0 => -30 + 3mu + 20 - 2*mu = 0 => mu - 10 = 0.

Step 7 (Final Result): lambda = 3 and mu = 10.




