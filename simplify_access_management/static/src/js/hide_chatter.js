/** @odoo-module **/

var FormRenderer = require('web.FormRenderer');
import { session } from "@web/session";
const Session = require("web.Session");
const { patch } = require("@web/core/utils/patch");
var rpc = require('web.rpc');

FormRenderer.include({
    init: function (parent, data, options) {
        const self = this;
        this._super.apply(this, arguments);

        var hash = window.location.hash.substring(1);
        hash = JSON.parse('{"' + hash.replace(/&/g, '","').replace(/=/g,'":"') + '"}', function(key, value) { return key===""?value:decodeURIComponent(value) })
        rpc.query({
             model:'access.management',
             method: 'get_chatter_hide_details',
             args: [session.user_id, parseInt(hash.cids.charAt(0)), hash.model]
        }).then(function(result){
            if(result['hide_send_mail'] == false)
            {
                var btn1 = setInterval(function() {
                   if ($('.o_ChatterTopbar_buttonSendMessage').length) {
                        $('.o_ChatterTopbar_buttonSendMessage').remove();
                        clearInterval(btn1);
                   }
                }, 50);
            }
            if(result['hide_log_notes'] == false)
            {
                var btn2 = setInterval(function() {
                   if ($('.o_ChatterTopbar_buttonLogNote').length) {
                        $('.o_ChatterTopbar_buttonLogNote').remove();
                        clearInterval(btn2);
                   }
                }, 50);
            }
            if(result['hide_schedule_activity'] == false)
            {
                var btn3 = setInterval(function() {
                   if ($('.o_ChatterTopbar_buttonScheduleActivity').length) {
                        $('.o_ChatterTopbar_buttonScheduleActivity').remove();
                        clearInterval(btn3);
                   }
                }, 50);
            }

        });
    },
});