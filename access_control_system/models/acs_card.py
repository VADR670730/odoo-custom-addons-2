# -*- coding: utf-8 -*-
import json
import requests
import logging
import datetime
import random
from datetime import timedelta, date
from odoo import fields, models,api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

from .acs import write_card_log

_logger = logging.getLogger(__name__)

class AcsCard(models.Model):
    _name = 'acs.card'
    _description = '卡片設定'
    _rec_name = 'uid'
    confirmUnlink = fields.Boolean(string='確認刪除', default=False)

    uid = fields.Char(string='卡片號碼', required=True)
    pin = fields.Char(string='卡片密碼')
    status = fields.Selection([ ('新建', '新建'),('啟用', '啟用'),('作廢', '作廢')],'卡片狀態', default='新建', required=True)

    user_role = fields.Selection([ ('員工', '員工'),('客戶', '客戶'),('廠商', '廠商'),],'身份', default='客戶', required=True)
    partner_id = fields.Many2one('res.partner','持卡人', default=False)
    employee_id = fields.Many2one('hr.employee','員工', default=False)
    
    user_code = fields.Char(string='I D')
    user_name = fields.Char(string='名稱')
    user_phone = fields.Char(string='電話')
    #卡片被授權進入的門禁群組
    devicegroup_ids = fields.Many2many(
        string='授權門禁群組',
        comodel_name='acs.devicegroup',
        relation='acs_devicegroup_acs_card_rel',
        column1='devicegroup_id',
        column2='card_id',
    )
    #卡片被授權的合約清單
    contract_ids = fields.Many2many(
        string='合約清單',
        comodel_name='acs.contract',
        relation='acs_contract_acs_card_rel',
        column1='contract_id',
        column2='card_id',
    )

    def action_create_contract(self):
        #raise UserError('Not support yet,action_create_contract.')
        for record in self:
            form_id = record.env.ref('access_control_system.acs_contract_form_create').id
            _logger.warning('form_id: %s' % ( form_id ) )
            return {
                "type": "ir.actions.act_window",
                "res_model": "acs.contract",
                "name": "新建合約",
                'view_type':'form',
                'view_mode':'form',
                "views": [[form_id, "form"]],
                "target": "new",
                "context": {  
                    'default_partner_id' :  record.partner_id.id,
                },
            }

    def action_get_pin(self):
        for record in self:

            if len(self.devicegroup_ids) == 0 and len(self.contract_ids) == 0:
                raise UserError('尚未授權合約或群組，無法設定密碼')

            _logger.warning('產生密碼: %s' % (record.uid) )
            new_pin = ''
            while new_pin =='' :
                test_pin = str( random.randint(1000,9999) )
                logs = self.env['acs.accesscodelog'].sudo().search(
                    [ ('accesscode','=', test_pin ) ,('expire_time','>',datetime.datetime.now() ) ] )
                for log in logs:
                    _logger.warning('重複的密碼: %s' % (log) )
                    new_pin = ''
                    continue
                new_pin = test_pin
            #確認密碼產生
            record.pin = new_pin

    # @api.constrains('uid')
    # def check_uid(self):
    #     for record in self:
    #         _logger.warning('check_uid: %s' % (record.uid) )
    #         card2add = self.env['acs.card'].sudo().search([['uid','=',record.uid ] ])
    #         _logger.warning('check_uid: %s' % (card2add.uid) )
    #         # if card2add :
    #         #     raise ValidationError('已存在同樣的卡片號碼')

    def action_dispose(self):
        #raise UserError('Not support yet,action_dispose.')
        for record in self:
            _logger.warning('作廢: %s' % (record.uid) )
            record.status ="作廢"

    @api.onchange('user_role')
    def _change_user_role(self):
        for record in self:
            if record.status !='新建':
                raise ValidationError('已啟用的卡片無法更改持有人，請作廢或新增卡片。')
            else:
                if record.user_role == '廠商':
                    record.employee_id = False
                    return {'domain': {'partner_id': [('supplier_rank', '>', 0)]}}
                if record.user_role == '客戶':
                    record.employee_id = False
                    return {'domain': {'partner_id': [('supplier_rank', '=', 0)]}}
                if record.user_role == '員工':
                    record.partner_id = False

    @api.onchange('partner_id')
    def _update_partner_profile(self):
        for record in self:
            if record.partner_id:
                record.user_name = record.partner_id.name
                record.user_phone = record.partner_id.phone
                record.user_code = record.partner_id.vat #統編 身份證

    @api.onchange('employee_id')
    def _update_employee_profile(self):
        for record in self:
            if record.employee_id:
                record.user_name = record.employee_id.name
                record.user_phone = record.employee_id.work_phone
                record.user_code = record.employee_id.barcode #徽章 ID, 工號

#card ORM methods
    @api.model
    def create(self, vals):
        #_logger.warning('create self: %s' % (self) )
        #_logger.warning('create vals: %s' % (vals) )

        if 'status' in vals:
            if vals['status'] == '新建':
                vals['status'] ='啟用'
        
        if ('partner_id' in vals):
            if vals['partner_id']:
                record = self.env['res.partner'].sudo().search([ ['id','=',vals['partner_id'] ] ] )
                vals['user_name'] = record.name
                vals['user_phone'] = record.phone
                vals['user_code'] = record.vat #統編 身份證
        
        if ('employee_id' in vals):
            if vals['employee_id']:
                record = self.env['hr.employee'].sudo().search([ ['id','=',vals['employee_id'] ] ])
                vals['user_name'] = record.name
                vals['user_phone'] = record.work_phone
                vals['user_code'] = record.barcode #徽章 ID, 工號

        if ('partner_id' in vals and vals['partner_id'] == False ) and ( 'employee_id' in vals and vals['employee_id'] == False) :
            raise ValidationError("必須指定持卡人")

        write_card_log(self ,vals)
        result = super(AcsCard, self).create(vals)
        return result

    def write(self,vals):
        for record in self:
            vals['user_role'] = record.user_role
            if record.employee_id:
                vals['user_name'] = record.employee_id.name
                vals['user_phone'] = record.employee_id.work_phone
                vals['user_code'] = record.employee_id.barcode #徽章 ID, 工號            
            if record.partner_id:
                vals['user_name'] = record.partner_id.name
                vals['user_phone'] = record.partner_id.phone
                vals['user_code'] = record.partner_id.vat #統編 身份證            
            
            write_card_log(self ,vals)
            result = super(AcsCard, self).write(vals)
            return result

    def unlink(self):
        if self.confirmUnlink:
            result = super(AcsCard, self).unlink()
            return result
        else:
            raise ValidationError("禁止未確認的刪除")

