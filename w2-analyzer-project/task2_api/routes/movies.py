from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import httpx
import os
from typing import Optional, List, Dict, Any
from task2_api.dependencies import get_movie_api_key

router = APIRouter()

class Movie(BaseModel):
    title: str
    director: str

class MoviesResponse(BaseModel):
    movies: List[Movie]
    page: int
    total_pages: int
    total_results: int

@router.get("/movies", response_model=MoviesResponse)
async def get_movies(
    q: Optional[str] = Query(None, description="Search keyword"),
    page: int = Query(1, ge=1, description="Page number")
):
    """
    Search movies by keyword using The Movie Database API
    """
    if not q:
        return MoviesResponse(
            movies=[],
            page=page,
            total_pages=0,
            total_results=0
        )
    
    api_key = get_movie_api_key()
    base_url = "https://api.themoviedb.org/3/search/movie"
    
    # Configure timeout and retry
    timeout = httpx.Timeout(10.0, connect=5.0)
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            # First attempt
            response = await client.get(
                base_url,
                params={
                    "api_key": api_key,
                    "query": q,
                    "page": page,
                    "language": "en-US"
                }
            )
            
            # Retry once if failed
            if response.status_code >= 500:
                response = await client.get(
                    base_url,
                    params={
                        "api_key": api_key,
                        "query": q,
                        "page": page,
                        "language": "en-US"
                    }
                )
            
            response.raise_for_status()
            data = response.json()
            
            # Extract movies with directors
            movies = []
            for movie_data in data.get("results", []):
                # Get director information
                director = await get_movie_director(movie_data["id"], api_key, client)
                
                movies.append(Movie(
                    title=movie_data.get("title", "Unknown"),
                    director=director or "Unknown"
                ))
            
            return MoviesResponse(
                movies=movies,
                page=data.get("page", 1),
                total_pages=data.get("total_pages", 0),
                total_results=data.get("total_results", 0)
            )
            
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=502, 
                detail=f"Upstream API error: {e.response.status_code}"
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=502, 
                detail=f"Failed to connect to movie API: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Internal server error: {str(e)}"
            )

async def get_movie_director(movie_id: int, api_key: str, client: httpx.AsyncClient) -> str:
    """
    Get director for a movie (simplified implementation)
    """
    try:
        response = await client.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}/credits",
            params={"api_key": api_key}
        )
        
        if response.status_code == 200:
            credits = response.json()
            crew = credits.get("crew", [])
            directors = [person for person in crew if person.get("job") == "Director"]
            if directors:
                return directors[0].get("name", "Unknown")
    except:
        pass
    
    return "Unknown"