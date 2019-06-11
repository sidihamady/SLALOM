// ======================================================================================================
// SLALOM - Open-Source Solar Cell Multivariate Optimizer
// Copyright(C) 2012-2019 Sidi OULD SAAD HAMADY (1,2,*), Nicolas FRESSENGEAS (1,2). All rights reserved.
// (1) Université de Lorraine, Laboratoire Matériaux Optiques, Photonique et Systèmes, Metz, F-57070, France
// (2) Laboratoire Matériaux Optiques, Photonique et Systèmes, CentraleSupélec, Université Paris-Saclay, Metz, F-57070, France
// (*) sidi.hamady@univ-lorraine.fr
// SLALOM source code is available to download from:
// https://github.com/sidihamady/SLALOM
// https://hal.archives-ouvertes.fr/hal-01897934
// http ://www.hamady.org/photovoltaics/slalom_source.zip
// Cite as: S Ould Saad Hamady and N Fressengeas, EPJ Photovoltaics, 9:13, 2018.
// See Copyright Notice in COPYRIGHT
// ======================================================================================================

// ------------------------------------------------------------------------------------------------------
// File:      InGaN_Bandgap.c
// Type:      C module
// Purpose:   Bandgap model for InGaN
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
    /* In the Deckbuild input REGION statement put x.comp=$AlloyComp */

    const double ega = (xcomp * egalpha_InN) + ((1.0 - xcomp) * egalpha_GaN);
    const double egb = (xcomp * egbeta_InN) + ((1.0 - xcomp) * egbeta_GaN);

    *eg = (xcomp * eg300_InN) + ((1.0 - xcomp) * eg300_GaN) - (BowingBandgap * xcomp * (1.0 - xcomp));
    *chi = (xcomp * affinity_InN) + ((1.0 - xcomp) * affinity_GaN) - (BowingAffinity * xcomp * (1.0 - xcomp));
    *nc = (xcomp * nc300_InN) + ((1.0 - xcomp) * nc300_GaN);
    *nv = (xcomp * nv300_InN) + ((1.0 - xcomp) * nv300_GaN);
    *degdt = ((-2.0 * ega * temp * (temp + egb)) + (ega * temp * temp)) / ((temp + egb) * (temp + egb));

    return 0;
}
