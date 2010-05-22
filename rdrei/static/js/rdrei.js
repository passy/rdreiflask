/**
 * rdrei.js
 * ~~~~~~~~
 *
 * Known Bugs
 * ==========
 * 
 * - Home does not load if you start from a different entry point.
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
        activeClass: "active",
        slideEffect: false,
        titlePrefix: "rdrei.net \u2014 ",
        defaultTitle: "Pascal Hartig"
    },

    _create: function () {
        var that = this,
            loaded = false;

        $.address.crawlable(this.options.crawlable);
        // Globally enabled.
        $().address();
        // Save the initial color.
        this._init_colorchanger();
        $.address.init(function (event) {
            if (event.value != '/') {
                loaded = true;
            }
        }).change(function (event) {
            if (loaded) {
                that._onChange(event);
            } else {
                loaded = true;
            }
        });
        this._log("Initialized address topMenu content loader.");
    },

    _init_colorchanger: function () {
        var $body = $("body");
        $body.data('color', $body.attr('class'));
    },

    // Activates the menu entry with the given url.
    _activate: function (url) {
        var className = this.options.activeClass,
            oldEntry, newEntry,
            oldIndex, newIndex;

        this._log("Searching for URL ", url);

        oldEntry = this.element.find("a." + className).removeClass(className);
        newEntry = this.element.find("a[href~='" + url + "']:last").addClass(className);

        if (oldEntry) {
            // Check how the elements are related.
            oldIndex = oldEntry.parent().index();
            newIndex = newEntry.parent().index();

            // Is left of the old.
            return (oldIndex > newIndex);
        }
    },

    _showContent: function (data, direction) {
        var $endpoint = $(this.options.target),
            that = this;

        function replace() {
            $endpoint.html(data);

            var $wrapper = $endpoint.children(1),
            color = $wrapper.attr("data-color"),
            title = $wrapper.attr("data-title"),
            newTitle = that.options.titlePrefix + 
                that.options.defaultTitle;

            if (that.options.slideEffect) {
                that._log("Showing content with slide effect.");
                $endpoint.show('slide', {
                    direction: direction
                }, function () {
                    that._trigger('content-visible');
                });
            } else {
                that._trigger('content-visible');
            }


            if (color) {
                $("body").colorChanger(color);
            }
            if (title) {
                newTitle = that.options.titlePrefix + title;
            }
            // $.address.title is useless.
            window.document.title = newTitle;

            that._trigger('loaded');
        }

        if (!this.options.slideEffect || this._slidedOut) {
            // Replace right now.
            this._log("Instantly replacing content.");
            replace();
        } else {
            // Not slided out yet, load later.
            $endpoint.one('slided-out', function () {
                that._log("Delayed replacing of content.");
                replace();
            });
        }
    },

    _onChange: function (event) {
        var $endpoint = $(this.options.target),
            url = event.path + "?ajax",
            that = this,
            // Boolean that stores from where the slide comes.
            fromRight,
            direction;

        fromRight = that._activate(event.value);
        // You can override the sliding direction by the _slide url parameter.
        if ('_slide' in event.parameters && 
            event.parameters._slide === "right") {
            fromRight = true;
        }

        direction = fromRight ? 'right' : 'left';

        if (this.options.slideEffect) {
            this._slidedOut = false;
            $endpoint.hide('slide', {direction: direction}, function () {
                this._slidedOut = true;
                $(this).trigger('slided-out');
            });
        }

        this._log("Loading url ", url);
        $.get(url, function (data) {
            // Check for colors.
            var direction = fromRight ? 'left' : 'right';

            that._log("Content received.");
            that._showContent(data, direction);
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
        previousColor = this.data('color');

    if (Modernizr.cssanimations) {
        // Remove previously applied color.
        if (previousColor) {
            this.removeClass(previousColor);
        }
        this.addClass(color);
    } else {
        if (previousColor) {
            this.removeClass(previousColor);
        }
        // Reset previous animation. Won't look too good, I guess. \:
        this.addClass(color, settings.duration / 2);
    }

    // Save the currently applied color.
    this.data('color', color);

    return this;
};

$.fn.loadDisqus = function (url) {
    var $iframe = $("<iframe />", {
        'src': url,
        'id': "disqus-frame"
    }).appendTo(this);
    $iframe.animate({
        minHeight: 500
    }, 2000);
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

    // Initialize notify
    $("#notify-container").notify();
    // Check for previously printed notifications.
    $("#global-flash li").each(function () {
        var text = $(this).text();
        if (text) {
            $("#notify-container").notify("create", {
                title: "Benachrichtigung",
                text: $(this).text()
            });
        }
    });
});
