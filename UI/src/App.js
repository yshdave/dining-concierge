import React from 'react';
import './App.css';
import { Router, Route , Switch} from "react-router-dom";
import Chat from './Pages/Chat';
import 'bootstrap/dist/css/bootstrap.min.css';
import history from './history';

function App() {
  return (
    <div className="App fill">
      <header className="header">
      </header>
      <div className="content fill">
        <Router history={history}>
          <Switch>
            <Route exact path="/" component={Chat} />
          </Switch>
        </Router>
      </div>
      <footer className="footer">
      </footer>
    </div>
  );
}

export default App;
