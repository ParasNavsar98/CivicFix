"""
Phase 1 — Embedding Similarity Experiment
Evaluates BAAI/bge-small-en-v1.5 on 15 CivicFix-style problem pairs:
- 5 Genuine Duplicate / Paraphrase pairs (DUPLICATE)
- 5 Related but non-duplicate pairs (RELATED_NON_DUPLICATE)
- 5 Clearly different pairs (DIFFERENT)

Prints normalized cosine similarity scores to observe distribution.
NOTE: This is an experiment only — DO NOT use to hardcode production thresholds.
"""

from sentence_transformers import SentenceTransformer, util


def run_experiment():
    print("=" * 80)
    print("CIVICFIX — EMBEDDING SIMILARITY EXPERIMENT (BAAI/bge-small-en-v1.5)")
    print("=" * 80)

    # Load model once
    model = SentenceTransformer("BAAI/bge-small-en-v1.5")
    print(f"Model loaded successfully. Embedding dimension: {model.get_sentence_embedding_dimension()}\n")

    # 1. Genuine Duplicate / Paraphrase Pairs (5 pairs)
    duplicates = [
        (
            "Garbage is being burned near a school, producing harmful smoke.",
            "Unprocessed waste is being burned close to the school and causing air pollution."
        ),
        (
            "Potholes on Main Street near the central market are causing heavy traffic and minor accidents.",
            "Deep road craters near the central market on Main St are creating traffic jams and vehicle damage."
        ),
        (
            "Drinking water pipeline broken near Sector 4 community hall, causing severe water leakage.",
            "Water supply pipe has burst in front of Sector 4 community center, wasting clean water."
        ),
        (
            "Primary health center lacks basic emergency medicines and essential first-aid supplies.",
            "The local primary health facility has a shortage of critical emergency drugs and first-aid kits."
        ),
        (
            "Frequent unexpected power outages occurring in the industrial zone during peak working hours.",
            "Unannounced electricity supply cuts happening repeatedly in the industrial estate in working hours."
        ),
    ]

    # 2. Related but NOT Duplicate Pairs (5 pairs)
    related_non_duplicates = [
        (
            "Garbage is being burned near a school, producing harmful smoke.",
            "Garbage collection trucks are not visiting the neighborhood regularly, leaving bins overflowing."
        ),
        (
            "Drinking water pipeline broken near Sector 4 community hall, causing severe water leakage.",
            "Water supply in Sector 4 is contaminated with brown silt and smells bad when faucets are turned on."
        ),
        (
            "Potholes on Main Street near the central market are causing heavy traffic and minor accidents.",
            "Streetlights on Main Street near the central market are not working, making the road dark at night."
        ),
        (
            "Primary health center lacks basic emergency medicines and essential first-aid supplies.",
            "Primary health center building roof is leaking water during heavy rainfall."
        ),
        (
            "Agricultural crop storage facility lacks refrigeration equipment for post-harvest preservation.",
            "Farmers are facing shortage of certified seeds and fertilizers for the upcoming sowing season."
        ),
    ]

    # 3. Clearly Different Pairs (5 pairs)
    different = [
        (
            "Garbage is being burned near a school, producing harmful smoke.",
            "Primary health center lacks basic emergency medicines and essential first-aid supplies."
        ),
        (
            "Potholes on Main Street near the central market are causing heavy traffic and minor accidents.",
            "Farmers are facing shortage of certified seeds and fertilizers for the upcoming sowing season."
        ),
        (
            "Drinking water pipeline broken near Sector 4 community hall, causing severe water leakage.",
            "High school lacks qualified computer science teachers and functioning desktop computers."
        ),
        (
            "Frequent unexpected power outages occurring in the industrial zone during peak working hours.",
            "Public hospital blood bank requires urgent blood donors for rare blood groups."
        ),
        (
            "Unprocessed municipal waste dumped in the local river polluting water source.",
            "Subsidized grain distribution at the public distribution shop was delayed this month."
        ),
    ]

    categories = [
        ("DUPLICATE", duplicates),
        ("RELATED_NON_DUPLICATE", related_non_duplicates),
        ("DIFFERENT", different),
    ]

    summary_stats = {}

    for cat_name, pairs in categories:
        print("-" * 80)
        print(f" CATEGORY: {cat_name}")
        print("-" * 80)
        scores = []
        for i, (text_a, text_b) in enumerate(pairs, 1):
            emb_a = model.encode(text_a, normalize_embeddings=True, convert_to_tensor=True)
            emb_b = model.encode(text_b, normalize_embeddings=True, convert_to_tensor=True)
            similarity = util.cos_sim(emb_a, emb_b).item()
            scores.append(similarity)

            print(f"Pair #{i} [{cat_name}] — Cosine Similarity: {similarity:.4f}")
            print(f"  Text A: {text_a}")
            print(f"  Text B: {text_b}")
            print()

        avg_score = sum(scores) / len(scores)
        min_score = min(scores)
        max_score = max(scores)
        summary_stats[cat_name] = (min_score, avg_score, max_score)

    print("=" * 80)
    print("SUMMARY STATISTICAL OBSERVED RANGES (NOT PRODUCTION THRESHOLDS):")
    print("=" * 80)
    for cat_name, (mn, avg, mx) in summary_stats.items():
        print(f"  {cat_name:<25} Min: {mn:.4f} | Avg: {avg:.4f} | Max: {mx:.4f}")
    print("=" * 80)


if __name__ == "__main__":
    run_experiment()
