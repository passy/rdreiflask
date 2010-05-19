/**
 * rdrei_admin.js
 * ~~~~~~~~~~~~~~
 * 
 * Adds admin functionality.
 *
 * :copyright: 2010, Pascal Hartig <phartig@rdrei.net>
 * :license: GPL v3, see doc/LICENSE for more details.
 */

/*global $ */
/*jslint white: true, onevar: true, browser: true, undef: true, nomen: true, eqeqeq: true, plusplus: true, bitwise: true, regexp: true, strict: true, newcap: true */
"use strict";

$(function () {
    $("header nav").bind("topmenucontent-visible", function () {
        $(".admin-corner").fadeIn();
    });
});
