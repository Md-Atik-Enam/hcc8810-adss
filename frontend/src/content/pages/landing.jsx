import axios from 'axios';
import { Component } from "react";
import { Button, Container, Form, Row, Spinner } from "react-bootstrap";
import { Navigate } from "react-router-dom";
import { API } from '../utils/constants';

class LandingPage extends Component
{
	constructor(props)
	{
		super(props);
		this.state = {
			username: undefined,
			updateSuccess: false,
			loading: false,
			userResponded: false,
		}
		this.userSession = this.createOrGetUser.bind(this);
		this.simulateLogin = this.startTimer.bind(this);
	}

	// TODO implement this!
	createOrGetUser()
	{
		this.setState({
			loading: true
		});

		let username = this.state.username;

		axios.post(API + 'create_or_get_user', {
			username: username,
			response: {}
		},
			{
				headers: {
					'Access-Control-Allow-Credentials': true,
					'Access-Control-Allow-Origin': '*'
				}
			})
			.then(response =>
			{
				if (response.status === 200)
				{
					this.setState({
						updateSuccess: true,
						loading: false
					});
				}
			});
	}

	async startTimer()
	{
		await this.wait(3000);
		this.setState({
			updateSuccess: true
		});
	}

	wait(time)
	{
		this.setState({
			loading: true
		});
		return new Promise(resolve =>
		{
			setTimeout(resolve, time);
		});
	}

	onValueChange = (event) =>
	{
		let responseText = event.target.value;
		this.setState({
			username: responseText,
			userResponded: responseText.length > 1
		});
	}

	render()
	{
		let buttonDisabled = !this.state.userResponded;
		let username = this.state.username;

		const dest = this.props.dest;

		if (this.state.updateSuccess)
		{
			return (
				<Navigate to={dest} state={
					{
						// username: username
						userid: 1
					}
				} />
			);
		}

		return (
			<div style={{ marginTop: "144px", textShadow: "0.18px .18px gray" }}>
				<Container>
					<Row>
						<h3>Welcome to the Recommender System for Self Actualization.</h3>
					</Row>
					<Row>
						<Form.Group className="mb-3" controlId="responseText">
							<Form.Label>Enter a username we can associate you with for personalizing recommendations.</Form.Label>
							<Form.Control as="textarea" rows={1} onChange={this.onValueChange} />
						</Form.Group>
					</Row>
				
					<Row>
						<Button variant="primary" size="md" className="footer-btn"
							disabled={buttonDisabled && !this.state.loading}
							// onClick={this.userSession}
							onClick={this.simulateLogin}
						>
							{!this.state.loading ? 'Next'
								:
								<>
									<Spinner
										as="span"
										animation="grow"
										size="sm"
										role="status"
										aria-hidden="true"
									/>
									Loading...
								</>
							}
						</Button>
					</Row>
				</Container>
			</div>
		)
	}
}

export default LandingPage;