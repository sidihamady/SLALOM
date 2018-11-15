// ======================================================================================================
// SLALOM - Open-Source Solar Cell Multivariate Optimizer
// Copyright(C) 2012-2018 Sidi OULD SAAD HAMADY (1,2,*), Nicolas FRESSENGEAS (1,2). All rights reserved.
// (1) Université de Lorraine, Laboratoire Matériaux Optiques, Photonique et Systèmes, Metz, F-57070, France
// (2) Laboratoire Matériaux Optiques, Photonique et Systèmes, CentraleSupélec, Université Paris-Saclay, Metz, F-57070, France
// (*) sidi.hamady@univ-lorraine.fr
// Version: 1.0 Build: 1811
// SLALOM source code is available to download from:
// https://github.com/sidihamady/SLALOM
// https://hal.archives-ouvertes.fr/hal-01897934v1
// http ://www.hamady.org/photovoltaics/slalom_source.zip
// See Copyright Notice in COPYRIGHT
// ======================================================================================================

// ------------------------------------------------------------------------------------------------------
// File: InGaN_Permittivity.c
// Type: C module
// Purposes: Permittivity model for InGaN
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
    /* In the Deckbuild input REGION statement put x.comp=$AlloyComp */

    *eps = (xcomp * permittivity_InN) + ((1.0 - xcomp) * permittivity_GaN);

    return 0;
}
