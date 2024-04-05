/* Copyright 2021-2025
 * This file is part of HULK.
 *
 * HULK is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * HULK is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with HULK.  If not, see <http://www.gnu.org/licenses/>.
 */
#include <stdio.h>
#include <math.h>

/* IO */

int h_printn (double n)
{
  return (printf("%lf\n", n), 0);
}

int h_prints (char* v)
{
  return (printf("%s\n", v), 0);
}

/* MATH */

double h_cos (double n) { return cos (n); }
double h_exp (double n) { return exp (n); }
double h_log (double a, double b) { return log (a) / log (b); }
double h_pow (double a, double b) { return pow (a, b); }
double h_sin (double n) { return sin (n); }
double h_sqrt (double n) { return sqrt (n); }
