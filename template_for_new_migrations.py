from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('Loanapp', 'previous_migration'),
    ]

    def check_if_table_exists(apps, schema_editor):
        table_name = 'your_table_name'
        return table_name in schema_editor.connection.introspection.table_names()

    def check_if_column_exists(apps, schema_editor, table_name, column_name):
        with schema_editor.connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT COUNT(*)
                FROM information_schema.columns 
                WHERE table_name='{table_name}'
                AND column_name='{column_name}'
                """
            )
            return cursor.fetchone()[0] > 0

    operations = [
        # Skip table creation if exists
        migrations.RunPython(
            code=lambda apps, schema_editor: None if check_if_table_exists(apps, schema_editor) else None,
            reverse_code=migrations.RunPython.noop,
        ),

        # Add new columns only if they don't exist
        migrations.RunPython(
            code=lambda apps, schema_editor: (
                migrations.AddField(
                    model_name='your_model',
                    name='new_field',
                    field=models.CharField(max_length=100, null=True),
                ) if not check_if_column_exists(apps, schema_editor, 'your_table', 'new_field') else None
            ),
            reverse_code=migrations.RunPython.noop,
        ),
    ] 