/** @odoo-module **/

var ListRenderer = require('web.ListRenderer');
import { session } from "@web/session";
const Session = require("web.Session");
const { patch } = require("@web/core/utils/patch");
var rpc = require('web.rpc');

ListRenderer.include({
    init: function (parent, data, options) {
        const self = this;
        this._super.apply(this, arguments);

        var hash = window.location.hash.substring(1);
        hash = JSON.parse('{"' + hash.replace(/&/g, '","').replace(/=/g,'":"') + '"}', function(key, value) { return key===""?value:decodeURIComponent(value) })
        rpc.query({
             model:'access.management',
             method: 'is_export_hide',
             args: [session.user_id, parseInt(hash.cids.charAt(0)), hash.model]
        }).then(function(result){
            debugger
            if(result) {
                debugger
                var btn1 = setInterval(function() {
                   if ($('.o_list_export_xlsx').length) {
                        $('.o_list_export_xlsx').remove();
                        clearInterval(btn1);
                   }
                }, 50);
            }

        });
    },
});