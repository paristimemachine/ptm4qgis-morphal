# translation update
# update .ts translation files, compile to .qm
translation_update:
	pylupdate5 -verbose morphal/resources/i18n/plugin_translation.pro
	lrelease morphal/resources/i18n/*.ts
