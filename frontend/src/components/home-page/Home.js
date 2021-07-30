import React, { useState, useEffect } from "react";
import Container from "@material-ui/core/Container";
import AuctionItem from "./AuctionItem";
import Filter from "./Filter";
import Pagination from "../helpers/Pagination";
import { getItems } from "../../authorization/apiCalls";

export default function Home(props) {
  const page = props.match.params.page;

  const [items, setItems] = useState([]);
  const [order, setOrder] = useState("-created_date");
  const [paginator, setPaginator] = useState(1);

  useEffect(() => {
    getItems(order, page)
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
  }, [page, order]);

  return (
    <div>
      <Container component="main" maxWidth="xs">
        <Filter />
        {items.length > 0 &&
          items.map((item) => {
            return (
              <AuctionItem
                key={item.id}
                title={item.title}
                description={item.description}
                compressed_picture={item.compressed_picture}
              />
            );
          })}
        <Pagination {...props} count={paginator} />
      </Container>
    </div>
  );
}
