/**
 * rdrei.js
 * ~~~~~~~~
 *
 * :copyright: date, Pascal Hartig <phartig@rdrei.net>
 * :license: GPL v3, see doc/LICENSE for more details.
 */

/*global $, window, document */
/*jslint white: true, onevar: true, browser: true, undef: true, nomen: true, eqeqeq: true, plusplus: true, bitwise: true, regexp: true, strict: true, newcap: true */
"use strict";

jQuery.Widget.prototype._log = function () {
    var args = Array.prototype.slice.call(arguments),
        newArgs = [[this.namespace, this.widgetName].join('.') + ": "].concat(args);

    if (window.console && window.console.log) {
        window.console.log.apply(window.console, newArgs);
    }
};

$.widget("rdrei.topMenu", {
    options: {
        crawlable: true,
        target: "#ajax-endpoint",
        activeClass: "active"
    },

    _create: function () {
        var that = this;

        $.address.crawlable(this.options.crawlable);
        this.element.find("a").address();
        $.address.change(function (event) {
            that._onChange(event);
        });
        this._log("Initialized address topMenu content loader.");
    },

    // Activates the menu entry with the given url.
    _activate: function (url) {
        var className = this.options.activeClass;
        // Exception for '/' because it's replaced by address.
        if (url === '/') {
            url = '#';
        }

        this.element.find("a").removeClass(className).
            filter("[href$='" + url + "']").addClass(className);
    },

    _onChange: function (event) {
        var $endpoint = $(this.options.target),
            url = event.value + "?ajax",
            that = this;

        this._log("Loading url ", url);
        $endpoint.load(url, function () {
            // Check for colors.
            var color = $endpoint.children(1).attr("data-color");
            if (color) {
                $("body").colorChanger(color);
            }
            that._activate(event.value);
        });
    }
});

/**
 * Changes the body color and uses either css animations or jquery ui color
 * fading.
 */
$.fn.colorChanger = function (color, options) {
    var settings = $.extend({}, options, {
        duration: 5000
    }),
        that = this,
        previousColor = this.data('color');

    function removePreviousColor() {
        // Remove previously applied color.
        if (previousColor) {
            console.log("Found color: ", previousColor);
            that.removeClass(previousColor);
        }
    }

    if (Modernizr.cssanimations) {
        removePreviousColor();
        this.addClass(color);
    } else {
        removePreviousColor();
        this.stop().addClass(color, settings.duration);
    }

    // Save the currently applied color.
    this.data('color', color);

    return this;
};

$(document).ready(function () {
    $("header nav").topMenu();
    // Show the loading indicator
    $("#loading").ajaxStart(function () {
        $(this).show();
    }).ajaxStop(function () {
        $(this).hide();
    }).ajaxError(function () {
        alert("An error occured. Please check your network settings.");
    });
});
