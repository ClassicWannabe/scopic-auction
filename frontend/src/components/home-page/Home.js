import React, { useState, useEffect } from "react";
import Container from "@material-ui/core/Container";
import Grid from "@material-ui/core/Grid";
import AuctionItem from "./ItemList";
import Filter from "./Filter";
import Pagination from "../helpers/Pagination";
import { getItems } from "../../api/apiCalls";
import "./Home.css";

export default function Home(props) {
  const page = props.match.params.page;

  const [items, setItems] = useState([]);
  const [filter, setFilter] = React.useState(() => {
    return { init_bid: "", created_date: "-created_date", search: "" };
  });
  const [paginator, setPaginator] = useState(1);

  useEffect(() => {
    const cleanFilter = Object.fromEntries(
      Object.entries(filter).filter(([_, v]) => v !== null && v !== "")
    );
    if (cleanFilter.init_bid && cleanFilter.created_date) {
      cleanFilter.ordering = `${cleanFilter.init_bid},${cleanFilter.created_date}`;
      delete cleanFilter.init_bid;
      delete cleanFilter.created_date;
    } else if (cleanFilter.init_bid) {
      cleanFilter.ordering = cleanFilter.init_bid;
      delete cleanFilter.init_bid;
    } else if (cleanFilter.created_date) {
      cleanFilter.ordering = cleanFilter.created_date;
      delete cleanFilter.created_date;
    }

    getItems(cleanFilter, page)
      .then((response) => {
        if (
          response !== undefined &&
          response.status === 200 &&
          response.data.results?.length > 0
        ) {
          setItems(response.data.results);
          setPaginator(
            Math.ceil(response.data.count / response.data.page_size)
          );
        }
      })
      .catch((error) => console.error(error));
  }, [page, filter]);

  return (
    <Container component="main">
      <Filter setFilter={setFilter} />
      <Grid container spacing={3} justifyContent="center">
        {items.length > 0 &&
          items.map((item) => {
            return (
              <AuctionItem
                {...props}
                key={item.id}
                id={item.id}
                title={item.title}
                description={item.description}
                compressedPicture={item.compressed_picture}
                initBid={item.init_bid}
              />
            );
          })}
      </Grid>
      <Pagination {...props} count={paginator} page={page} />
    </Container>
  );
}
