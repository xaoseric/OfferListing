# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Plan.virtualization'
        db.add_column(u'offers_plan', 'virtualization',
                      self.gf('django.db.models.fields.CharField')(default='o', max_length=1),
                      keep_default=False)

        # Adding field 'Plan.bandwidth'
        db.add_column(u'offers_plan', 'bandwidth',
                      self.gf('django.db.models.fields.BigIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Plan.disk_space'
        db.add_column(u'offers_plan', 'disk_space',
                      self.gf('django.db.models.fields.BigIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Plan.memory'
        db.add_column(u'offers_plan', 'memory',
                      self.gf('django.db.models.fields.BigIntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Plan.virtualization'
        db.delete_column(u'offers_plan', 'virtualization')

        # Deleting field 'Plan.bandwidth'
        db.delete_column(u'offers_plan', 'bandwidth')

        # Deleting field 'Plan.disk_space'
        db.delete_column(u'offers_plan', 'disk_space')

        # Deleting field 'Plan.memory'
        db.delete_column(u'offers_plan', 'memory')


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
            'disk_space': ('django.db.models.fields.BigIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'memory': ('django.db.models.fields.BigIntegerField', [], {}),
            'offer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['offers.Offer']"}),
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