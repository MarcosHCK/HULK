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
#include <math.h>
#include <stdio.h>
#include <stdint.h>

typedef struct _Object Object;

struct _Object
{
  uint32_t typeid;
};

/* IO */

int print_number_boolean (double n)
{
  return (printf ("%lf\n", n), 1);
}

int print_string_boolean(char *v)
{
  return (printf ("%s\n", v), 1);
}

/* MATH */

double cos_number_number (double n) { return cos (n); }
double exp_number_number (double n) { return exp (n); }
double log_number_number_number (double a, double b) { return log (a) / log (b); }
double pow_number_number_number (double a, double b) { return pow (a, b); }
double sin_number_number (double n) { return sin (n); }
double sqrt_number_number (double n) { return sqrt (n); }

/* Typing */

Object* object_ctor (Object* object)
{
  object->typeid = 0;
  return object;
}
