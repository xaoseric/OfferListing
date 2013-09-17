# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Plan.ipv4_space'
        db.add_column(u'offers_plan', 'ipv4_space',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)

        # Adding field 'Plan.ipv6_space'
        db.add_column(u'offers_plan', 'ipv6_space',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Plan.billing_time'
        db.add_column(u'offers_plan', 'billing_time',
                      self.gf('django.db.models.fields.CharField')(default='m', max_length=1),
                      keep_default=False)

        # Adding field 'Plan.promo_code'
        db.add_column(u'offers_plan', 'promo_code',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'Plan.cost'
        db.add_column(u'offers_plan', 'cost',
                      self.gf('django.db.models.fields.DecimalField')(default=1.0, max_digits=20, decimal_places=2),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Plan.ipv4_space'
        db.delete_column(u'offers_plan', 'ipv4_space')

        # Deleting field 'Plan.ipv6_space'
        db.delete_column(u'offers_plan', 'ipv6_space')

        # Deleting field 'Plan.billing_time'
        db.delete_column(u'offers_plan', 'billing_time')

        # Deleting field 'Plan.promo_code'
        db.delete_column(u'offers_plan', 'promo_code')

        # Deleting field 'Plan.cost'
        db.delete_column(u'offers_plan', 'cost')


    models = {
        u'offers.offer': {
            'Meta': {'object_name': 'Offer'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['offers.Provider']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'d'", 'max_length': '1'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'offers.plan': {
            'Meta': {'object_name': 'Plan'},
            'bandwidth': ('django.db.models.fields.BigIntegerField', [], {}),
            'billing_time': ('django.db.models.fields.CharField', [], {'default': "'m'", 'max_length': '1'}),
            'cost': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'disk_space': ('django.db.models.fields.BigIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipv4_space': ('django.db.models.fields.IntegerField', [], {}),
            'ipv6_space': ('django.db.models.fields.IntegerField', [], {}),
            'memory': ('django.db.models.fields.BigIntegerField', [], {}),
            'offer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['offers.Offer']"}),
            'promo_code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'virtualization': ('django.db.models.fields.CharField', [], {'default': "'o'", 'max_length': '1'})
        },
        u'offers.provider': {
            'Meta': {'object_name': 'Provider'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['offers']