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

disconnected_signal_info = []

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
    disconnected_signal_info.append({
        'signal': post_save,
        'receiver': post_save_receiver,
        'sender': model
    })

    # Disconnect post_delete
    post_delete.disconnect(receiver=post_delete_receiver, sender=model)
    disconnected_signal_info.append({
        'signal': post_delete,
        'receiver': post_delete_receiver,
        'sender': model
    })

print("Loading data dump...")

try:
    call_command("loaddata", "data_dump.json")
    print("Data loaded successfully.")
except Exception as e:
    print(f"An error occurred during data loading: {e}")
    sys.exit(1)
finally:
    # Always reconnect signals in a finally block
    print("Reconnecting Elasticsearch signals...")
    for sig_info in disconnected_signal_info:
        sig_info['signal'].connect(
            receiver=sig_info['receiver'],
            sender=sig_info['sender']
        )
    print("Elasticsearch signals reconnected.")

    # After loading data, you MUST rebuild your Elasticsearch indexes.
    # This will attempt to connect to 'es-nexus', so ensure your hosts file is correct.
    print("Rebuilding Elasticsearch indexes...")
    try:
        call_command("search_index", "--rebuild")
        print("Elasticsearch indexes rebuilt successfully.")
    except Exception as rebuild_e:
        print(f"An error occurred during Elasticsearch index rebuilding: {rebuild_e}")
        # Don't exit here, as the data load itself might have been successful.
        # Just notify about the index rebuild issue.