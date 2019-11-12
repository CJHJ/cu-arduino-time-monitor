import React, { Component } from 'react';

const globalBestScore = 8.124;

const Teams = (props) => (
    <div>
        <table className="table">
            <tbody>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Beginner Score</th>
                    <th>Advanced Time</th>
                    <th>Advanced Score</th>
                    <th>Total Score</th>
                </tr>
                {
                    props.rows.map(function (x, i) {
                        var mtime = parseFloat(x['mtime']);

                        const advScore = (40.0 * globalBestScore / mtime) + 10.0;
                        var totalScore = Math.max(advScore, parseFloat(x['bscore']));

                        if (isNaN(mtime)) {
                            totalScore = parseFloat(x['bscore']);
                        }
                        return <Team key={i} data={x} advScore={advScore} totalScore={totalScore} />
                    }).sort(function (firstTemp, secondTemp) {
                        const first = firstTemp.props.data;
                        const second = secondTemp.props.data;

                        var firstMtime = parseFloat(first['mtime']);
                        // firstMtime = isNaN(firstMtime) ? Infinity : firstMtime;
                        var secondMtime = parseFloat(second['mtime']);
                        // secondMtime = isNaN(secondMtime) ? Infinity : secondMtime;

                        const firstAdvScore = (40.0 * globalBestScore / firstMtime) + 10.0;
                        var firstTotalScore = Math.max(firstAdvScore, parseFloat(first['bscore']));

                        const secondAdvScore = (40.0 * globalBestScore / secondMtime) + 10.0;
                        var secondTotalScore = Math.max(secondAdvScore, parseFloat(second['bscore']));

                        if (isNaN(firstMtime)) {
                            firstTotalScore = parseFloat(first['bscore']);
                        }
                        if (isNaN(secondMtime)) {
                            secondTotalScore = parseFloat(second['bscore']);
                        }

                        console.log(firstMtime)

                        return firstTotalScore > secondTotalScore ? -1 : (firstTotalScore < secondTotalScore ? 1 : 0);
                    })
                }
            </tbody>
        </table>
    </div>
)

const Team = (props) => (
    <tr>
        <td>{props.data['id']}</td>
        <td>{props.data['name']}</td>
        <td>{props.data['bscore']}</td>
        <td>{props.data['mtime']}</td>
        <td>{Number(props.advScore.toFixed(2))}</td>
        <td>{Number(props.totalScore.toFixed(2))}</td>
    </tr>
)

export default class Home extends Component {
    constructor(props) {
        super(props);
        this.state = {
            isRecording: false,
            currentTeam: 0,
            teams: [],
        };

        // Refs
        this.recordStartButton = React.createRef();
        this.recordStopButton = React.createRef();

        this.handleTeamChange = this.handleTeamChange.bind(this);
        this.handleStartRecording = this.handleStartRecording.bind(this);
        this.handleStopRecording = this.handleStopRecording.bind(this);
    }

    componentDidMount() {
        fetch('http://127.0.0.1:5000/get_teams')
            .then(res => res.json())
            .then((res) => {
                console.log(res);
                this.setState({
                    teams: res,
                });
            });
    }

    handleTeamChange(event) {
        const team = event.target.value;
        this.setState({
            currentTeam: team
        });
    }

    handleStartRecording() {
        this.recordStartButton.current.setAttribute("disabled", "disabled");

        const data = { current_team: this.state.currentTeam };

        fetch('http://127.0.0.1:5000/start_recording', {
            method: 'POST',
            headers: {
                'Content-type': 'application/json',
            },
            body: JSON.stringify(data),
        })
            .then(res => res.json())
            .then((res) => {
                this.recordStartButton.current.removeAttribute("disabled");
                this.setState({
                    isRecording: true,
                });
                console.log(res);
            });
    }

    handleStopRecording() {
        this.recordStopButton.current.setAttribute("disabled", "disabled");

        const data = { "data": "test" };

        fetch('http://127.0.0.1:5000/stop_recording', {
            method: 'POST',
            headers: {
                'Content-type': 'application/json',
            },
            body: JSON.stringify(data),
        })
            .then(res => res.json())
            .then((res) => {
                this.recordStopButton.current.removeAttribute("disabled");
                this.setState({
                    isRecording: false,
                });
                console.log(res);
            });
    }

    render() {
        let recordButton;

        if (!this.state.isRecording) {
            recordButton = <button className="btn btn-primary" ref={this.recordStartButton} onClick={this.handleStartRecording}>Start Recording</button>
        } else {
            recordButton = <button className="btn btn-warning" ref={this.recordStopButton} onClick={this.handleStopRecording}>Stop Recording</button>
        }

        return (
            <div className="main-container">
                <h1>Ranking</h1>
                <input
                    className="form-control current-input"
                    type="text"
                    value={this.state.currentTeam}
                    onChange={this.handleTeamChange}
                />
                {recordButton}
                <Teams rows={this.state.teams} />
            </div>
        )
    }
}