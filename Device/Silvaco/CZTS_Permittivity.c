/* (C) Sidi HAMADY */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <ctype.h>
#include <malloc.h>
#include <string.h>

#include "CZTS_Parameters.h"

/*
 * Composition and temperature dependent permitivity.
 * Statement: MATERIAL
 * Parameter: F.EPSILON
 * Arguments:
 * xcomp    composition fraction x
 * ycomp    composition fraction y
 * temp     temperature (K)
 * *eps     relative permitivity
 */
int epsilon(double xcomp, double ycomp, double temp, double *eps)
{
   *eps = permittivity_CZTS;

   return 0;
}