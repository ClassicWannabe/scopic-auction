import React, { useState } from "react";
import Avatar from "@material-ui/core/Avatar";
import Button from "@material-ui/core/Button";
import CssBaseline from "@material-ui/core/CssBaseline";
import TextField from "@material-ui/core/TextField";
import LockOutlinedIcon from "@material-ui/icons/LockOutlined";
import Typography from "@material-ui/core/Typography";
import { makeStyles } from "@material-ui/core/styles";
import Container from "@material-ui/core/Container";
import { getToken, getUserDetails } from "../../authorization/apiCalls";

const useStyles = makeStyles((theme) => ({
  paper: {
    marginTop: theme.spacing(8),
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
  },
  avatar: {
    margin: theme.spacing(1),
    backgroundColor: theme.palette.secondary.main,
  },
  form: {
    width: "100%",
    marginTop: theme.spacing(1),
  },
  submit: {
    margin: theme.spacing(3, 0, 2),
  },
}));

export default function Login(props) {
  const classes = useStyles();

  const [credentials, setCredentials] = useState(() => {
    return { username: "", password: "" };
  });

  function handleChange(event) {
    const { name, value } = event.target;

    setCredentials((prevValues) => {
      return { ...prevValues, [name]: value };
    });
  }

  function handleSubmit(event) {
    event.preventDefault();

    getToken(credentials)
      .then((response) => {
        if (response && response.status == 200) {
          localStorage.setItem("token", response.data.token);

          setCredentials({ username: "", password: "" });
        }
        return response
      })
      .then((response) => {
        if (response.data?.token) {
          getUserDetails(response.data.token).then((response) => {
            if (response && response.status == 200) {
              localStorage.setItem("user_id", response.data.id);
              localStorage.setItem(
                "max_auto_bid",
                response.data.max_auto_bid_amount
              );
  
              window.location.href = "/";
            }
          });
        }
        
      })
      .catch((error) => console.error(error));
  }

  return (
    <Container component="main" maxWidth="xs">
      <CssBaseline />
      <div className={classes.paper}>
        <Avatar className={classes.avatar}>
          <LockOutlinedIcon />
        </Avatar>
        <Typography component="h1" variant="h5">
          Sign in
        </Typography>
        <form onSubmit={handleSubmit} className={classes.form} noValidate>
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            id="username"
            label="Username"
            name="username"
            autoComplete="username"
            autoFocus
            onChange={handleChange}
            value={credentials.username}
          />
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            name="password"
            label="Password"
            type="password"
            id="password"
            autoComplete="current-password"
            onChange={handleChange}
            value={credentials.password}
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            color="primary"
            className={classes.submit}
          >
            Sign In
          </Button>
        </form>
      </div>
    </Container>
  );
}
