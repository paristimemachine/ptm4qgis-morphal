# -*- coding: utf-8 -*-

"""
/***************************************************************************
    morphal_angle_utils.py
    Part of the Paris Time Machine plugin for QGIS
    --------------
    Date                 : January 2021
    Copyright            : (C) 2021, Eric Grosso, Paris Time Machine
    Email                : eric dot ptm at thefactory dot io
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Eric Grosso'
__date__ = 'January 2021'
__copyright__ = '(C) 2021, Eric Grosso, Paris Time Machine'

import math

from qgis.core import (QgsDistanceArea,
                       QgsGeometry,
                       QgsLineString,
                       QgsPoint,
                       QgsPolygon)


	/**
	 * Compute the angle between 2 {@link Point}s (between 0 and PI or between O and PI/2)
	 * comparatively to the X axis.
	 *
	 * @param point first point of the angle
	 * @param point2 point to process
	 * @param unit unit in degree if 0, grade if 2
	 * @param interval interval [ 0 ; PI [ if 0, [ 0 ; PI/2 [ if 1,
	 * 		  otherwise the interval [ 0 ; PI/2 [ is the default choice
	 * @param accuracy true to keep two numbers after the dot, false to keep all numbers
	 * @return the computed angle
	 */
	public static double angle(Point point, Point point2, int unit, int interval, boolean accuracy) {
		double x = point2.getX() - point.getX();
		double y = point2.getY() - point.getY();
		double angle = Math.atan2(y,x);

		// [O ; Pi[
		if (interval == AngleUtil.ZERO_PI) {
			if (angle < 0) angle = angle + Math.PI;
			if (angle == Math.PI) angle = 0.0;
		} else { // [O ; Pi/2[ (by choice or by default)
			if (angle < 0) angle = angle + Math.PI;
			angle = angle % (Math.PI / 2.0);
			if (angle == Math.PI/2.0) angle = 0.0;
		}

		// Convert into the chosen unit
		if (unit == AngleUtil.DEGRE) {
			angle = Math.toDegrees(angle);
		} else if (unit == AngleUtil.GRADE) {
			angle = angle * 200.0 / Math.PI;
		}

		if (accuracy) {
			// TODO 2020 check / find a way to improve
			angle = new Long(Math.round(angle * 100)).doubleValue() / 100.0;
//			Long.valueOf(Math.round(angle * 100)).doubleValue();
//			angle = (double)Math.round(angle * 100) / 100.0; // a priori the best option (to test)
		}

		return angle;
	}
