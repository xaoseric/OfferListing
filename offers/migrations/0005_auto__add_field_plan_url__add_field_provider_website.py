# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Plan.url'
        db.add_column(u'offers_plan', 'url',
                      self.gf('django.db.models.fields.TextField')(default='http://example.com'),
                      keep_default=False)

        # Adding field 'Provider.website'
        db.add_column(u'offers_provider', 'website',
                      self.gf('django.db.models.fields.URLField')(default='http://example.com', max_length=255),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Plan.url'
        db.delete_column(u'offers_plan', 'url')

        # Deleting field 'Provider.website'
        db.delete_column(u'offers_provider', 'website')


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
            'url': ('django.db.models.fields.TextField', [], {}),
            'virtualization': ('django.db.models.fields.CharField', [], {'default': "'o'", 'max_length': '1'})
        },
        u'offers.provider': {
            'Meta': {'object_name': 'Provider'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['offers']