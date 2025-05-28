import sys
import os
import django
from django.db.models.signals import post_save, post_delete
from django_elasticsearch_dsl.registries import registry
from django.core.management import call_command

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nexus.settings")

django.setup()

print("Temporarily disconnecting Elasticsearch signals...")

# Iterate through all registered documents
for doc_class in registry.get_documents():
    # Instantiate the document to get its methods
    doc_instance = doc_class()
    model = doc_class.django.model # The model associated with this document

    # The actual methods connected as receivers are `update` and `delete`
    # on the instance of the Document class.
    post_save_receiver = doc_instance.update
    post_delete_receiver = doc_instance.delete

    # Disconnect post_save
    post_save.disconnect(receiver=post_save_receiver, sender=model)

    # Disconnect post_delete
    post_delete.disconnect(receiver=post_delete_receiver, sender=model)

print("Loading data dump...")

try:
    call_command("loaddata", "data_dump.json")
    print("Data loaded successfully.")

except Exception as e:
    print(f"An error occurred during data loading: {e}")
    sys.exit(1)