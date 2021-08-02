import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
import Home from "./home-page/Home";
import Login from "./login-page/Login";
import AuctionItemDetail from "./item-detail-page/ItemDetail";
import "./App.css";

function App() {
  return (
    <div className="App">
      <Router>
        <Switch>
          <Route path="/login" render={(props) => <Login {...props} />} />
          <Route
            path="/item/:itemId"
            render={(props) => <AuctionItemDetail {...props} />}
          />
          <Route exact path="/" render={(props) => <Home {...props} />} />
          <Route path="/:page" render={(props) => <Home {...props} />} />
        </Switch>
      </Router>
    </div>
  );
}

export default App;
