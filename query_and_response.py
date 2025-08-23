def query_documents(collection, questions, n_results=5):
    """Query the collection for relevant documents and return both chunks and metadata"""
    results = collection.query(
        query_texts=questions, 
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )
    
    # Debug information to help diagnose the issue
    print(f"Query results structure: {list(results.keys())}")
    if "distances" in results:
        print(f"First few distances: {results['distances'][0][:3] if results['distances'] and len(results['distances']) > 0 and len(results['distances'][0]) > 0 else 'No distances found'}")
    
    # Organize results into a structured format with source information
    organized_results = []
    
    if not results["documents"] or len(results["documents"]) == 0 or len(results["documents"][0]) == 0:
        print("No documents found in query results")
        return organized_results
    
    # ChromaDB uses cosine distance by default (0 = identical, 2 = completely different)
    # First, get all distances to understand their range
    all_distances = []
    for dist_list in results["distances"]:
        all_distances.extend(dist_list)
    
    # Find min and max for normalization if needed
    min_distance = min(all_distances) if all_distances else 0
    max_distance = max(all_distances) if all_distances else 2  # Cosine distance max is 2
    distance_range = max_distance - min_distance if max_distance != min_distance else 1
    
    print(f"Distance range: min={min_distance}, max={max_distance}")
    
    for i in range(len(results["documents"][0])):
        # Get the distance value
        distance = results["distances"][0][i]
        
        # For cosine distance: 0 means identical, 2 means opposite
        # Convert to a 0-100 relevance scale where 100 is most relevant
        
        # ChromaDB uses cosine distance: 0 = identical, 2 = completely different
        # Convert to a relevance percentage where 100% = perfect match
        relevance_score = 1 - (distance / 2)  # Normalize to 0-1 range
        relevance_percentage = int(relevance_score * 100)  # Convert to percentage
        
        print(f"Document {i}: Distance={distance}, Score={relevance_score}, Percentage={relevance_percentage}%")
        
        organized_results.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "relevance_score": relevance_score,
            "relevance_percentage": relevance_percentage
        })
    
    # Sort by relevance score (highest first)
    organized_results.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    print("==== Returning relevant chunks ====")
    return organized_results

def generate_response(client, question, relevant_chunks):
    """Generate a response based on relevant chunks with source citations"""
    # Extract just the text for context
    context_texts = [chunk["text"] for chunk in relevant_chunks]
    context = "\n\n".join(context_texts)
    
    # Get unique sources with relevance scores and text snippets for citation
    sources_with_scores = {}
    for chunk in relevant_chunks:
        source = chunk["source"]
        # Keep the highest relevance score for each source
        if source not in sources_with_scores or chunk["relevance_score"] > sources_with_scores[source]["score"]:
            # Get a snippet of the text (first 100 characters)
            text_snippet = chunk["text"][:150] + "..." if len(chunk["text"]) > 150 else chunk["text"]
            
            sources_with_scores[source] = {
                "score": chunk["relevance_score"],
                "percentage": chunk["relevance_percentage"],
                "text_snippet": text_snippet
            }
    
    # Format sources with scores and text snippets
    sources_info = []
    for source, info in sources_with_scores.items():
        sources_info.append({
            "name": source,
            "relevance": info["percentage"],
            "text_snippet": info["text_snippet"]
        })
    
    # Sort by relevance score
    sources_info.sort(key=lambda x: x["relevance"], reverse=True)
    
    # Calculate overall relevance score
    # Use a weighted average where the first result has more influence
    if relevant_chunks:
        # Apply weights to the top results (first result has highest weight)
        weights = [0.5, 0.3, 0.2]  # Weights for top 3 results
        
        # Ensure we don't go out of bounds
        num_chunks = min(len(relevant_chunks), len(weights))
        
        # Calculate weighted average
        weighted_sum = 0
        for i in range(num_chunks):
            weighted_sum += relevant_chunks[i]["relevance_percentage"] * weights[i]
        
        # Round to nearest integer
        overall_relevance = int(weighted_sum)
        print(f"Overall relevance score: {overall_relevance}%")
    else:
        overall_relevance = 0
        print("No relevant chunks found, setting overall relevance to 0")
    
    prompt = (
        "You are a specialized question-answering assistant that only responds based on the provided context. "
        "Follow these rules strictly:\n"
        "1. Only use information from the provided context to answer.\n"
        "2. If the context doesn't contain information to answer the question, respond with: 'I don't have information about this in my knowledge base.'\n"
        "3. Never make up or infer information not present in the context.\n"
        "4. Do not use any prior knowledge beyond the given context.\n"
        "5. Provide a clear, concise answer (3-5 sentences maximum).\n"
        "6. Do not mention that you're using 'context' or 'documents' in your answer.\n\n"
        f"Context:\n{context}\n\n"
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
            {
                "role": "user",
                "content": question,
            },
        ],
    )

    answer = response.choices[0].message.content
    
    # Add sources and relevance info to the response
    final_response = {
        "answer": answer,
        "sources": sources_info[:5],  # Top 5 sources with relevance scores and text snippets
        "overall_relevance": overall_relevance  # Overall relevance score
    }
    
    print(f"Returning response with overall relevance: {overall_relevance}%")
    print(f"Source info example: {sources_info[0] if sources_info else 'No sources'}")
    
    return final_response
