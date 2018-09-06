// ======================================================================================================
// SLALOM - Open-Source Solar Cell Multivariate Optimizer
// Copyright(C) 2012-2018 Sidi OULD SAAD HAMADY (1,2,*), Nicolas FRESSENGEAS (1,2). All rights reserved.
// (1) Université de Lorraine, Laboratoire Matériaux Optiques, Photonique et Systèmes, Metz, F-57070, France
// (2) Laboratoire Matériaux Optiques, Photonique et Systèmes, CentraleSupélec, Université Paris-Saclay, Metz, F-57070, France
// (*) sidi.hamady@univ-lorraine.fr
// Version: 1.0 Build : 1807
// SLALOM source code is available to download here : http ://www.hamady.org/photovoltaics/slalom_source.zip
// See Copyright Notice in COPYRIGHT
// ======================================================================================================

// ------------------------------------------------------------------------------------------------------
// File:      InGaN_Index.c
// Type:      C module
// Purpose:   Refractive index model for InGaN
// Can be adapted for other compound semiconductor by changing the...
// ...InN_GaN_Parameters.h header and the model implementation
// ------------------------------------------------------------------------------------------------------

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <ctype.h>
#include <malloc.h>
#include <string.h>

#include "InN_GaN_Parameters.h"

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
    /* In the Deckbuild input REGION statement put x.comp=$AlloyComp */

    double Eph = 1.23984 / lambda;	/* Photon energy */
    double Eg;

    /* Parameters taken from:
    *   G.F. Brown et al.,
    *   "Finite element simulations of compositionally graded InGaN solar cells",
    *   Solar Energy Materials and Solar Cells 94 (2010) 478
    */
    double Ct[] = { 3.52517, 0.51672, 0.6094, 0.58108, 0.66796, 0.69642 },
        Dt[] = { -0.65710, 0.46836, 0.62182, 0.66902, 0.68886, 0.46055 },
        A, B, C, D, alpha;

    /* alpha0 checked by fitting GaN experimental absorption spectra from Appl. Phys. Lett. 71 (18) 1997 */
    double alpha0 = 1e5;

    /* Parameters taken from:
    *   Muhammad Nawaz et al.,
    *   "A TCAD-based modeling of GaN/InGaN/Si solar cells",
    *   Semicond. Sci. Technol. 27 (2012) 035019
    */
    Eg = (xcomp * eg300_InN) + ((1.0 - xcomp) * eg300_GaN) - (BowingBandgap * xcomp * (1.0 - xcomp));
    C = 3.525016201 - (18.297594473 * xcomp) + (40.221588785 * xcomp * xcomp) - (37.52274528 * xcomp * xcomp * xcomp) + (12.772362503 * xcomp * xcomp * xcomp * xcomp);
    D = -0.665086247 + (3.616441372 * xcomp) - (2.460307692 * xcomp * xcomp);
    if (Eph >= Eg) {
        alpha = alpha0 * sqrt((C * (Eph - Eg)) + (D * (Eph - Eg) * (Eph - Eg))); /* absorption (cm^-1) */
    }
    else {
        alpha = 0.0;
    }
    *k = lambda * (1e-4) * alpha / (4.0 * 3.141592653589793);

    A = (13.55 * xcomp) + (9.31 * (1.0 - xcomp));
    B = (2.05 * xcomp) + (3.03 * (1.0 - xcomp));
    if (Eph >= Eg) {
        *n = sqrt((A * 0.5857864376269) + B);
    }
    else {
        *n = sqrt((A * Eg * Eg * (2.0 - sqrt(1.0 + (Eph / Eg)) - sqrt(1.0 - (Eph / Eg))) / (Eph * Eph)) + B);
    }

    return 0;
}

/*
// testing
int main(void)
{
    double lambda = 0.4, n, k;

    int iOk = index(lambda, 300.0, 0.5, 0.0, 0.0, 0.0, 0.0, &n, &k);
    printf("lambda = %.2f   n = %.3f   k = %.3f   (iOk = %d)\n", lambda, n, k, iOk);

    return 0;
}
*/
