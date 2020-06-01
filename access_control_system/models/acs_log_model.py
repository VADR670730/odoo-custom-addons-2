# -*- coding: utf-8 -*-
import datetime
import requests
import json
from odoo import fields, models,api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

import logging
_logger = logging.getLogger(__name__)

class AcsServicelog(models.Model):
    _name = 'acs.servicelog'
    _description = '卡機通訊紀錄'
    #devicelog_id =  fields.Char(string='卡機紀錄編號', size=16 )
    
class AcsCardlog(models.Model):
    _name = 'acs.cardlog'
    _description = '刷卡紀錄'

    cardlog_id = fields.Char(string='紀錄編號')
    device_owner = fields.Char(string='門市')
    device_name = fields.Char(string='卡機名稱')
    user_role = fields.Char(string='身份')
    card_id = fields.Char(string='卡片號碼')
    cardlog_type = fields.Char(string='卡別')
    user_id = fields.Char(string='I D')
    user_name = fields.Char(string='名稱')
    cardlog_time = fields.Datetime(string='刷卡時間')
    cardlog_result = fields.Char(string='刷卡狀態')

class AcsEmployeeCardlog(models.Model):
    _name = 'acs.employeecardlog'
    _description = '員工打卡紀錄'

    employeecardlog_id = fields.Char(string='紀錄編號')
    device_owner = fields.Char(string='門市')
    device_name = fields.Char(string='卡機名稱')
    card_id = fields.Char(string='卡片號碼')
    user_id = fields.Char(string='I D')
    user_name = fields.Char(string='名稱')
    employeecardlog_type = fields.Char(string='刷卡狀態')
    employeecardlog_time = fields.Datetime(string='刷卡時間')

class AcsCardSettinglog(models.Model):
    _name = 'acs.cardsettinglog'
    _description = '卡片異動紀錄'

    cardsettinglog_id = fields.Char(string='紀錄編號')
    cardsetting_type = fields.Char(string='異動別')
    user_role = fields.Char(string='身份')
    user_id = fields.Char(string='I D')
    user_name = fields.Char(string='名稱')
    card_id = fields.Char(string='卡片號碼')
    cardsettinglog_time = fields.Datetime(string='變更時間')
    cardsettinglog_user = fields.Char(string='變更者')    

class AcsAccessCodelog(models.Model):
    _name = 'acs.accesscodelog'
    _description = '個人通關密碼設定紀錄'

    accesscodelog_id = fields.Char(string='紀錄編號')
    user_role = fields.Char(string='身份')
    user_id = fields.Char(string='I D')
    user_name = fields.Char(string='名稱')
    devicegroup_name = fields.Char(string='門禁群組')
    create_time = fields.Datetime(string='變更時間')
    expire_time = fields.Datetime(string='有效時間')
    accesscode = fields.Char(string='通關密碼')
