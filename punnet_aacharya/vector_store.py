import chromadb
from chromadb.config import Settings
import json
import logging
import os
from pathlib import Path
from config import VECTOR_DB_PATH, COLLECTION_NAME

logger = logging.getLogger(__name__)

class AstrologyKnowledgeBase:
    def __init__(self):
        logger.info("Initializing AstrologyKnowledgeBase")
        logger.info(f"Vector DB path: {VECTOR_DB_PATH}")
        logger.info(f"Collection name: {COLLECTION_NAME}")
        
        try:
            self.client = chromadb.PersistentClient(
                path=VECTOR_DB_PATH,
                settings=Settings(anonymized_telemetry=False)
            )
            logger.info("ChromaDB client created successfully")
            
            self.collection = self._get_or_create_collection()
            logger.info("Collection ready")
            
            self._load_knowledge_base()
            logger.info("Knowledge base loaded successfully")
            
        except Exception as e:
            logger.error(f"Error initializing AstrologyKnowledgeBase: {str(e)}")
            raise
    
    def _get_or_create_collection(self):
        """Get or create the collection"""
        logger.info("Getting or creating collection")
        try:
            collection = self.client.get_collection(COLLECTION_NAME)
            logger.info(f"Found existing collection: {COLLECTION_NAME}")
            return collection
        except Exception as e:
            logger.info(f"Collection not found, creating new collection: {COLLECTION_NAME}")
            collection = self.client.create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("New collection created successfully")
            return collection
    
    def _load_knowledge_files(self):
        """Load knowledge from JSON files in the knowledge directory"""
        knowledge_dir = Path("knowledge")
        rules = []
        
        if not knowledge_dir.exists():
            logger.warning("Knowledge directory not found")
            return rules
        
        # Load career rules
        career_file = knowledge_dir / "career_rules.json"
        if career_file.exists():
            try:
                with open(career_file, 'r', encoding='utf-8') as f:
                    career_data = json.load(f)
                
                for planet, careers in career_data.get("planetary_careers", {}).items():
                    for career in careers:
                        rule = {
                            "id": f"career_{planet}_{career.lower().replace(' ', '_')}",
                            "text": f"Strong {planet} in birth chart indicates success in {career} career",
                            "category": "career",
                            "subcategory": "planetary_careers",
                            "planet": planet,
                            "career": career,
                            "importance": "high"
                        }
                        rules.append(rule)
                
                logger.info(f"Loaded {len(career_data.get('planetary_careers', {}))} career rules")
            except Exception as e:
                logger.error(f"Error loading career rules: {e}")
        
        # Load marriage rules
        marriage_file = knowledge_dir / "marriage_rules.json"
        if marriage_file.exists():
            try:
                with open(marriage_file, 'r', encoding='utf-8') as f:
                    marriage_data = json.load(f)
                
                for i, rule in enumerate(marriage_data.get("rules", [])):
                    rule_obj = {
                        "id": f"marriage_rule_{i+1}",
                        "text": f"{rule['condition']} - {rule['effect']}",
                        "category": "marriage",
                        "subcategory": "timing",
                        "condition": rule['condition'],
                        "effect": rule['effect'],
                        "strength": rule['strength'],
                        "importance": "high" if rule['strength'] > 0.8 else "medium"
                    }
                    rules.append(rule_obj)
                
                logger.info(f"Loaded {len(marriage_data.get('rules', []))} marriage rules")
            except Exception as e:
                logger.error(f"Error loading marriage rules: {e}")
        
        return rules
    
    def _load_knowledge_base(self):
        """Load astrological rules into vector database"""
        logger.info("Loading astrological rules into vector database")
        
        # Load rules from knowledge files
        file_rules = self._load_knowledge_files()
        
        # Additional comprehensive rules
        additional_rules = [
            # Marriage timing rules
            {
                "id": "marriage_jupiter_transit",
                "text": "Jupiter transit over natal Venus or 7th house indicates marriage timing",
                "category": "marriage",
                "subcategory": "timing",
                "importance": "high"
            },
            {
                "id": "marriage_7th_lord_dasha",
                "text": "When 7th lord is in favorable dasha/antardasha, marriage is likely",
                "category": "marriage",
                "subcategory": "timing",
                "importance": "high"
            },
            {
                "id": "marriage_venus_navamsa",
                "text": "Venus in 7th house of Navamsa indicates early marriage",
                "category": "marriage",
                "subcategory": "timing",
                "importance": "medium"
            },
            {
                "id": "marriage_saturn_aspect",
                "text": "Saturn aspect on 7th house may delay marriage",
                "category": "marriage",
                "subcategory": "timing",
                "importance": "high"
            },
            {
                "id": "marriage_jupiter_venus",
                "text": "Jupiter and Venus conjunction or mutual aspect favors marriage",
                "category": "marriage",
                "subcategory": "timing",
                "importance": "medium"
            },
            
            # Career guidance rules
            {
                "id": "career_10th_lord_d10",
                "text": "10th house lord in D10 chart determines career direction",
                "category": "career",
                "subcategory": "direction",
                "importance": "high"
            },
            {
                "id": "career_sun_10th",
                "text": "Strong Sun in 10th house indicates government or leadership roles",
                "category": "career",
                "subcategory": "direction",
                "importance": "high"
            },
            {
                "id": "career_mercury_10th",
                "text": "Mercury in 10th house favors business, communication, or analytical careers",
                "category": "career",
                "subcategory": "direction",
                "importance": "medium"
            },
            {
                "id": "career_mars_10th",
                "text": "Mars in 10th house indicates technical, engineering, or military careers",
                "category": "career",
                "subcategory": "direction",
                "importance": "medium"
            },
            {
                "id": "career_venus_10th",
                "text": "Venus in 10th house suggests artistic, creative, or luxury-related careers",
                "category": "career",
                "subcategory": "direction",
                "importance": "medium"
            },
            
            # Health and wellness
            {
                "id": "health_6th_house",
                "text": "6th house indicates health issues and enemies",
                "category": "health",
                "subcategory": "general",
                "importance": "high"
            },
            {
                "id": "health_mars_aspects",
                "text": "Mars aspects can indicate surgery or accidents",
                "category": "health",
                "subcategory": "accidents",
                "importance": "medium"
            },
            {
                "id": "health_saturn_6th",
                "text": "Saturn in 6th house may cause chronic health issues",
                "category": "health",
                "subcategory": "chronic",
                "importance": "high"
            },
            
            # Education and learning
            {
                "id": "education_4th_house",
                "text": "4th house indicates education and learning abilities",
                "category": "education",
                "subcategory": "general",
                "importance": "high"
            },
            {
                "id": "education_mercury_4th",
                "text": "Mercury in 4th house indicates strong analytical and learning abilities",
                "category": "education",
                "subcategory": "abilities",
                "importance": "medium"
            },
            {
                "id": "education_jupiter_4th",
                "text": "Jupiter in 4th house indicates wisdom and higher education",
                "category": "education",
                "subcategory": "wisdom",
                "importance": "medium"
            },
            
            # Financial prosperity
            {
                "id": "finance_2nd_house",
                "text": "2nd house indicates wealth and family finances",
                "category": "finance",
                "subcategory": "wealth",
                "importance": "high"
            },
            {
                "id": "finance_11th_house",
                "text": "11th house indicates income and gains",
                "category": "finance",
                "subcategory": "income",
                "importance": "high"
            },
            {
                "id": "finance_venus_2nd",
                "text": "Venus in 2nd house indicates luxury and material comforts",
                "category": "finance",
                "subcategory": "luxury",
                "importance": "medium"
            }
        ]
        
        # Combine all rules
        all_rules = file_rules + additional_rules
        logger.info(f"Total rules to load: {len(all_rules)}")
        
        # Add to vector database if not already present
        try:
            existing_ids = set(self.collection.get()['ids'])
            logger.info(f"Existing rules in database: {len(existing_ids)}")
        except Exception as e:
            logger.info("No existing rules found, starting fresh")
            existing_ids = set()
        
        documents = []
        metadatas = []
        ids = []
        
        for rule in all_rules:
            if rule['id'] not in existing_ids:
                documents.append(rule['text'])
                metadata = {
                    'category': rule['category'],
                    'importance': rule['importance']
                }
                if 'subcategory' in rule:
                    metadata['subcategory'] = rule['subcategory']
                if 'planet' in rule:
                    metadata['planet'] = rule['planet']
                if 'career' in rule:
                    metadata['career'] = rule['career']
                if 'strength' in rule:
                    metadata['strength'] = rule['strength']
                
                metadatas.append(metadata)
                ids.append(rule['id'])
                logger.debug(f"Adding rule: {rule['id']} - {rule['category']}")
        
        if documents:
            logger.info(f"Adding {len(documents)} new rules to database")
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info("Rules added successfully")
        else:
            logger.info("No new rules to add")
    
    def query_knowledge(self, query, category=None, n_results=5):
        """Query the knowledge base"""
        logger.info(f"Querying knowledge base: '{query[:50]}...'")
        logger.info(f"Category filter: {category}")
        logger.info(f"Number of results requested: {n_results}")
        
        try:
            where_clause = {"category": category} if category else None
            logger.debug(f"Where clause: {where_clause}")
            
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_clause
            )
            
            logger.info(f"Query completed, found {len(results['documents'][0])} results")
            logger.debug(f"Results: {results['documents'][0]}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error querying knowledge base: {str(e)}")
            return {"documents": [[]], "metadatas": [[]], "ids": [[]]}
    
    def get_astrological_guidance(self, chart_data, question, category=None):
        """Get astrological guidance based on birth chart and question"""
        logger.info(f"Getting astrological guidance for question: {question[:50]}...")
        logger.info(f"Category: {category}")
        
        # Extract relevant chart information
        ascendant = chart_data.get('ascendant_sign', 'Unknown')
        sun_sign = chart_data.get('sun_sign', 'Unknown')
        moon_sign = chart_data.get('moon_sign', 'Unknown')
        current_dasha = chart_data.get('dasha', {}).get('current_dasha', 'Unknown')
        
        # Create context-aware query
        context_query = f"{question} {ascendant} ascendant {sun_sign} sun {moon_sign} moon {current_dasha} dasha"
        
        # Query knowledge base
        results = self.query_knowledge(context_query, category, n_results=3)
        
        if not results['documents'][0]:
            logger.warning("No relevant astrological rules found")
            return "माफ़ कीजिए, इस प्रश्न के लिए कोई विशिष्ट ज्योतिषीय नियम नहीं मिला।"
        
        # Format the guidance
        guidance_parts = []
        for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
            importance = metadata.get('importance', 'medium')
            category = metadata.get('category', 'general')
            
            guidance_parts.append(f"• {doc}")
        
        guidance = "\n".join(guidance_parts)
        
        logger.info(f"Generated astrological guidance with {len(guidance_parts)} rules")
        return guidance 