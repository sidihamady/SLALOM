// ======================================================================================================
// SLALOM - Open-Source Solar Cell Multivariate Optimizer
// Copyright(C) 2012-2018 Sidi OULD SAAD HAMADY (1,2,*), Nicolas FRESSENGEAS (1,2). All rights reserved.
// (1) Université de Lorraine, Laboratoire Matériaux Optiques, Photonique et Systèmes, Metz, F-57070, France
// (2) Laboratoire Matériaux Optiques, Photonique et Systèmes, CentraleSupélec, Université Paris-Saclay, Metz, F-57070, France
// (*) sidi.hamady@univ-lorraine.fr
// SLALOM source code is available to download from:
// https://github.com/sidihamady/SLALOM
// https://hal.archives-ouvertes.fr/hal-01897934
// http ://www.hamady.org/photovoltaics/slalom_source.zip
// See Copyright Notice in COPYRIGHT
// ======================================================================================================

// ------------------------------------------------------------------------------------------------------
// File:      InGaN_Recomb.c
// Type:      C module
// Purpose:   Recombination model for InGaN
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
 * Electron SRH lifetime as a function of position
 * Statement: MATERIAL
 * Parameter: F.TAUN
 * Arguments:
 * x          location x (microns)
 * y          location y (microns)
 * temp       temperature (K)
 * nd         net concentration of donors (per cc)
 * na         net concentration of acceptors (per cc)
 * *taun      electron SRH lifetime (s)
 */
int taun(double x, double y, double temp, double nd, double na, double *taun)
{
    // SRH lifetime considered to be the same for GaN and InN
    const double xcomp = 0.50;

    *taun = (xcomp * taun0_InN) + ((1.0 - xcomp) * taun0_GaN);

    return 0;
}

/*
 * Hole SRH lifetime as a function of position
 * Statement: MATERIAL
 * Parameter: F.TAUP
 * Arguments:
 * x          location x (microns)
 * y          location y (microns)
 * temp       temperature (K)
 * nd         net concentration of donors (per cc)
 * na         net concentration of acceptors (per cc)
 * *taup      hole SRH lifetime (s)
 */
int taup(double x, double y, double temp, double nd, double na, double *taup)
{
    // SRH lifetime considered to be the same for GaN and InN
    const double xcomp = 0.50;

    *taup = (xcomp * taup0_InN) + ((1.0 - xcomp) * taup0_GaN);

    return 0;
}

/*
 * Radiative recombination rate as a function of composition and temperature.
 * Statement: MATERIAL
 * Parameter: F.COPT
 * Arguments:
 * temp       temperature (K)
 * xcomp      composition fraction x
 * ycomp      composition fraction y
 * *cop       radiative recomb. rate per cc per s
 */
int copt(double temp, double xcomp, double ycomp, double *cop)
{
    /* In the Deckbuild input REGION statement put x.comp=$AlloyComp */

    *cop = (xcomp * copt_InN) + ((1.0 - xcomp) * copt_GaN);

    return 0;
}

/*
 * Electron Auger rate as a function of composition and temperature.
 * Statement: MATERIAL
 * Parameter: F.GAUN
 * Arguments:
 * temp       temperature (K)
 * xcomp      composition fraction x
 * ycomp      composition fraction y
 * *gan       elect. Auger recomb. rate (cm^6/s)
 */
int gaun(double temp, double xcomp, double ycomp, double *gan)
{
    /* In the Deckbuild input REGION statement put x.comp=$AlloyComp */

    *gan = (xcomp * augn_InN) + ((1.0 - xcomp) * augn_GaN);

    return 0;
}

/*
 * Hole Auger rate as a function of composition and temperature.
 * Statement: MATERIAL
 * Parameter: F.GAUP
 * Arguments:
 * temp       temperature (K)
 * xcomp      composition fraction x
 * ycomp      composition fraction y
 * *gap       hole. Auger recomb. rate (cm^6/s)
 */
int gaup(double temp, double xcomp, double ycomp, double *gap)
{
    /* In the Deckbuild input REGION statement put x.comp=$AlloyComp */

    *gap = (xcomp * augp_InN) + ((1.0 - xcomp) * augp_GaN);

    return 0;
}
