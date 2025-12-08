import os
import shutil
from dotenv import load_dotenv
from pymongo import MongoClient
from pinecone import Pinecone

# Load environment variables
load_dotenv()

def reset_database():
    print("🗑️  Connecting to MongoDB...")
    MONGO_URI = os.getenv("MONGO_URI")
    DB_NAME = os.getenv("DB_NAME", "MedRagnosis")
    
    if not MONGO_URI:
        print("❌ Error: MONGO_URI not found in .env")
        return

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    # List of collections to clear
    collections = ["users", "reports", "diagnosis_history"]
    
    for col_name in collections:
        result = db[col_name].delete_many({})
        print(f"   - Deleted {result.deleted_count} documents from '{col_name}'")
    
    print("✅ MongoDB cleared.")

def reset_pinecone():
    print("\n🗑️  Connecting to Pinecone...")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "medragnosis-index")

    if not PINECONE_API_KEY:
        print("❌ Error: PINECONE_API_KEY not found in .env")
        return

    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(PINECONE_INDEX_NAME)
        
        # Delete all vectors in the namespace (empty namespace is default)
        index.delete(delete_all=True)
        print(f"✅ Pinecone index '{PINECONE_INDEX_NAME}' cleared.")
    except Exception as e:
        print(f"❌ Error clearing Pinecone: {e}")

def reset_local_files():
    print("\n🗑️  Cleaning local upload directory...")
    upload_dir = os.getenv("UPLOAD_DIR", "./uploaded_dir")
    
    if os.path.exists(upload_dir):
        # Remove all files in the directory but keep the directory itself
        for filename in os.listdir(upload_dir):
            file_path = os.path.join(upload_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"   ❌ Failed to delete {file_path}. Reason: {e}")
        print(f"✅ Local files in '{upload_dir}' deleted.")
    else:
        print(f"   ⚠️ Directory '{upload_dir}' does not exist, skipping.")

if __name__ == "__main__":
    confirm = input("⚠️  WARNING: This will DELETE ALL DATA (Users, Reports, History, Vectors). Type 'yes' to proceed: ")
    if confirm.lower() == "yes":
        reset_database()
        reset_pinecone()
        reset_local_files()
        print("\n✨ System Reset Complete! Start fresh by running the server.")
    else:
        print("❌ Operation cancelled.")