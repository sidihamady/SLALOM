/* (C) Sidi HAMADY */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <ctype.h>
#include <malloc.h>
#include <string.h>

#include "CZTS_Parameters.h"

/*
* Temperature and composition dependent band parameters
* Statement: MATERIAL
* Parameter: F.BANDCOMP
* Note:  This function can only be used with BLAZE.
* Arguments:
* xcomp   composition fraction "X"
* ycomp   composition fraction "Y"
* temp    temperature (K)
* *eg     return: band gap (eV)
* *chi    return: affinity (eV)
* *nc     return: conduction band density of states
* *nv     return: valence band density of states
* *degdt  return: derivative of Eg with respect to T
*/
int bandcomp(double xcomp, double ycomp, double temp, double *eg, double *chi, double *nc, double *nv, double *degdt)
{
   const double ega = egalpha_CZTS;
   const double egb = egbeta_CZTS;

   *eg = eg300_CZTS;
   *chi = affinity_CZTS;
   *nc = nc300_CZTS;
   *nv = nv300_CZTS;
   *degdt = ((-2.0 * ega * temp * (temp + egb)) + (ega * temp * temp)) / ((temp + egb) * (temp + egb));

   return 0;
}
