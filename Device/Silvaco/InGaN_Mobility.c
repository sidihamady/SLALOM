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
// File:      InGaN_Mobility.c
// Type:      C module
// Purpose:   Mobility model for InGaN
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
 * Composition, temperature and doping dependent electron mobility
 * Statement: MATERIAL
 * Parameter: F.CONMUN
 * Arguments:
 * xcomp      composition fraction x
 * ycomp      composition fraction y
 * temp       temperature (K)
 * nd         net concentration of donors (per cc)
 * na         net concentration of acceptors (per cc)
 * x          location x (microns)
 * y          location y (microns)
 * taun       electron SRH lifetime (s)
 * *mun       electron mobility
 */
int conmun(double xcomp, double ycomp, double temp, double nd, double na, double x, double y, double taun, double *mun)
{
    /* In the Deckbuild input REGION statement put x.comp=$AlloyComp */

    double tempa_InN = 1.0;
    double tempb_InN = 1.0;
    double tempc_InN = 1.0;
    double tempd_InN = 1.0;

    double tempa_GaN = 1.0;
    double tempb_GaN = 1.0;
    double tempc_GaN = 1.0;
    double tempd_GaN = 1.0;

    // InGaN
    double mu1n_InGaN = 1.0 / ((xcomp / mu1n_InN) + ((1.0 - xcomp) / mu1n_GaN));
    double mu2n_InGaN = 1.0 / ((xcomp / mu2n_InN) + ((1.0 - xcomp) / mu2n_GaN));
    double deltan_InGaN = (xcomp * deltan_InN) + ((1.0 - xcomp) * deltan_GaN);
    double ncritn_InGaN = (xcomp * ncritn_InN) + ((1.0 - xcomp) * ncritn_GaN);
    double tempa_InGaN = (xcomp * tempa_InN) + ((1.0 - xcomp) * tempa_GaN);
    double tempb_InGaN = (xcomp * tempb_InN) + ((1.0 - xcomp) * tempb_GaN);
    double tempc_InGaN = (xcomp * tempc_InN) + ((1.0 - xcomp) * tempc_GaN);
    double tempd_InGaN = (xcomp * tempd_InN) + ((1.0 - xcomp) * tempd_GaN);

    double tempa = pow(temp / 300.0, tempa_InGaN);
    double tempb = pow(temp / 300.0, tempb_InGaN);
    double tempc = pow(temp / 300.0, tempc_InGaN);
    double tempd = pow(temp / 300.0, tempd_InGaN);
    double Ntotal = nd + na;

    *mun = (mu1n_InGaN * tempa) + (((mu2n_InGaN * tempb) - (mu1n_InGaN * tempa)) / (1.0 + pow(Ntotal / (ncritn_InGaN * tempc), deltan_InGaN * tempd)));

    return 0;
}

/*
 * Composition, temperature and doping dependent hole mobility
 * Statement: MATERIAL
 * Parameter: F.CONMUP
 * Arguments:
 * xcomp      composition fraction x
 * ycomp      composition fraction y
 * temp       temperature (K)
 * nd         net concentration of donors (per cc)
 * na         net concentration of acceptors (per cc)
 * x          location x (microns)
 * y          location y (microns)
 * taup       hole SRH lifetime (s)
 * *mup       hole mobility
 */
int conmup(double xcomp, double ycomp, double temp, double nd, double na, double x, double y, double taup, double *mup)
{
    /* In the Deckbuild input REGION statement put x.comp=$xcomp */

    double tempa_InN = 1.0;
    double tempb_InN = 1.0;
    double tempc_InN = 1.0;
    double tempd_InN = 1.0;

    double tempa_GaN = 1.0;
    double tempb_GaN = 1.0;
    double tempc_GaN = 1.0;
    double tempd_GaN = 1.0;

    // InGaN
    double mu1p_InGaN = 1.0 / ((xcomp / mu1p_InN) + ((1.0 - xcomp) / mu1p_GaN));
    double mu2p_InGaN = 1.0 / ((xcomp / mu2p_InN) + ((1.0 - xcomp) / mu2p_GaN));
    double deltap_InGaN = (xcomp * deltap_InN) + ((1.0 - xcomp) * deltap_GaN);
    double ncritp_InGaN = (xcomp * ncritp_InN) + ((1.0 - xcomp) * ncritp_GaN);
    double tempa_InGaN = (xcomp * tempa_InN) + ((1.0 - xcomp) * tempa_GaN);
    double tempb_InGaN = (xcomp * tempb_InN) + ((1.0 - xcomp) * tempb_GaN);
    double tempc_InGaN = (xcomp * tempc_InN) + ((1.0 - xcomp) * tempc_GaN);
    double tempd_InGaN = (xcomp * tempd_InN) + ((1.0 - xcomp) * tempd_GaN);

    double tempa = pow(temp / 300.0, tempa_InGaN);
    double tempb = pow(temp / 300.0, tempb_InGaN);
    double tempc = pow(temp / 300.0, tempc_InGaN);
    double tempd = pow(temp / 300.0, tempd_InGaN);
    double Ntotal = nd + na;

    *mup = (mu1p_InGaN * tempa) + (((mu2p_InGaN * tempb) - (mu1p_InGaN * tempa)) / (1.0 + pow(Ntotal / (ncritp_InGaN * tempc), deltap_InGaN * tempd)));

    return 0;
}

