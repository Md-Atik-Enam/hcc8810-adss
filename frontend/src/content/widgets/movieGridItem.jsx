import React, { Component } from 'react';
import StarRatings from 'react-star-ratings';

const defaultMovieIco = require("../res/default_movie_icon.svg");

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"></link>

class MovieGridItem extends Component
{

	render()
	{

		let currentMovie = this.props.movieItem;
		let changeRating = this.props.ratingCallback;

		let containerClass = currentMovie.rating > 0 ? 'container-visited' : '';
		let starDivClass = currentMovie.rating > 0 ? 'star-div-rated' : 'star-div';

		return (
			<div id={"TN_" + currentMovie.movie_id}
				onMouseEnter={(evt) => this.props.hoverTracker(evt, currentMovie.movie_id, 'enter')}
				onMouseLeave={(evt) => this.props.hoverTracker(evt, currentMovie.movie_id, 'leave')}
				className={"grid-item " + containerClass} style={{
					backgroundImage: "url(" + currentMovie.poster + "), url('" + defaultMovieIco + "')",
				}}>
				<div className="overlay">
					{/*setRating() {
						changeRating = 5
					}
					return (
					<button onclick="setRating">Up</button>
					);

					setRatingDown() {
						changeRating = 1
					}
					return (
					<button onclick="setRatingDown">Down</button>
					);*/}


					<div className={starDivClass}>

						{<StarRatings
							rating={currentMovie.rating}
							starRatedColor="rgb(252,229,65)"
							starHoverColor="rgb(252,229,65)"
							starDimension="18px"
							starSpacing="1px"
							changeRating={changeRating}
							numberOfStars={5}
							name={currentMovie.movie_id}
						/>
						}

					</div>

					{/* <p style={{color: "white"}}>Yes | No</p> */}
				</div>
				<div className="grid-item-label" style={{ position: "absolute" }}>
					{currentMovie.title + " (" + currentMovie.year + ")"}
				</div>
			</div>
		);
	}
}

export default MovieGridItem;