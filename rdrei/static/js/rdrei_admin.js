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
    $("#admin-toggle-orientation").live('click', function () {
        $.get(this.href, function (data) {
            var $photoContainer = $(".photo-container");
            if (data == 'vertical' || data == 'horizontal') {
                $("#notify-container").notify("create", {
                    title: "Orientation changed",
                    text: "Photo orientation is now " + data
                });
                if (data == 'vertical') {
                    $photoContainer.removeClass("horizontal");
                } else {
                    $photoContainer.addClass("horizontal");
                }
            } else {
                $("#notify-container").notify("create", {
                    title: "Orientation change failed!",
                    text: "An error occured."
                });
            }
        });
        return false;
    });
});
