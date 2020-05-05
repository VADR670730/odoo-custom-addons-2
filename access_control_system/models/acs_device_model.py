# -*- coding: utf-8 -*-
from odoo import fields, models

class AcsDevice(models.Model):
    _name = 'acs.device'
    _description = '卡機設定'

    device_id = fields.Char(string="卡機編號", required=True)
    name = fields.Char(string="卡機名稱", required=True)
    device_ip =  fields.Char(string='IP 位址', size=15)
    device_type = fields.Char(string='型號', size=15)
    device_port = fields.Integer( string='卡機Port' )
    node_id = fields.Integer( string='卡機站號' )
    device_owner = fields.Char(string='門市', size=8)
    device_location = fields.Char(string='樓層', size=8)
    active = fields.Boolean('連線否', default=True)
    devicelog_id =  fields.Char(string='卡機紀錄編號', size=16 )

class AcsDeviceGroup(models.Model):
    _name = 'acs.devicegroup'
    _description = '門禁群組設定'

    devicegroup_id = fields.Char(string="群組編號", required=True)
    devicegroup_name = fields.Char(string="群組名稱", required=True)

class AcsCard(models.Model):
    _name = 'acs.card'
    _description = '卡片設定'

    user_role = fields.Char(string='身份', required=True)
    user_id = fields.Char(string='I D', required=True)
    user_name = fields.Char(string='名稱', required=True)
    user_phone = fields.Char(string='電話', required=True)
    card_id = fields.Char(string='卡片號碼', required=True)
    devicelog_id =  fields.Char(string='卡機紀錄編號', size=16 )

class AcsDeviceAccesscode(models.Model):
    _name = 'acs.deviceaccesscode'
    _description = '每日更新通關密碼'

    devicegroup_id = fields.Char(string="通用群組", required=True)
    devicegroup_name = fields.Char(string="群組名稱", required=True)
    accesscode = fields.Char(string="通關密碼", required=True)
    start_time = fields.Datetime(string='有效日期', required=True)
    end_time = fields.Datetime(string='失效日期')
    devicelog_id =  fields.Char(string='卡機紀錄編號', size=16 )
