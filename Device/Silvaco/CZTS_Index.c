/* (C) Sidi HAMADY */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <ctype.h>
#include <malloc.h>
#include <string.h>

/*
 *	Wavelength dependent complex index of refraction
 *	Statement: MATERIAL
 *	Parameter: F.INDEX
 *	Note: For raytracing (Luminous & Luminous3D) the arguments nconc, pconc
 *	and emag will be zeros.
 *	Arguments:
 *		lambda     wavelength (microns)
 *		temp       temperature (K)
 *		xcomp      composition fraction xcomp
 *		ycomp      composition fraction y
 *		nconc      electron concentration (1/cc)
 *		pconc      hole concentration (1/cc)
 *		emag       magnitude of electric field (V/cm)
 *		*n         real part of index of refraction
 *		*k         imaginary part of index of refraction
 */
int index(double lambda, double temp, double xcomp, double ycomp, double nconc, double pconc, double emag, double *n, double *k)
{
    double Eph = 1.23984 / lambda;
    double Eg = 1.5;
    double kA = 0.2;

    *n = 2.59;

    if (Eph >= Eg) {
        *k = (2.0 * Eg / Eph) * kA * sqrt((Eph - Eg) / Eg);
    }
    else {
        *k = 0.0;
    }

    return 0;
}
