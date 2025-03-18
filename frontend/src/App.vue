

// sudo npm run dev
// make HTTP request with axios
// Google: example post request from vue with axios



<script>

import axios from 'axios';

export default {
  data() {
    return {
      data_getMarket: null,
      data_getPrice: null,
      data_getAssets: null,

      data_createPerson: null,
      data_sell: null,
      data_buy: null,

      error: null,
    };
  },
  methods: {
    async getMarket() {
      try {
        const headers = { 'Content-Type': 'application/json' };
        const params = { 'resource_type': 'apple' };

        const response = await axios({
          method: 'get',
          url: 'http://127.0.0.1:5000/get_market',
          headers: headers,
          params: params,
        });

        console.log(response.data);

        this.data_getMarket = response.data;
        this.error = null;
      } catch (err) {
        this.data_getMarket = null;
        this.error = err.message;
      }
    },

    async getPrice() {
      try {
        const headers = { 'Content-Type': 'application/json' };
        const params = { 'resource_type': 'apple',
                         'amount': 1 };

        const response = await axios({
          method: 'get',
          url: 'http://127.0.0.1:5000/get_price',
          headers: headers,
          params: params,
        });

        console.log(response.data);

        this.data_getPrice = response.data;
        this.error = null;
      } catch (err) {
        this.data_getPrice = null;
        this.error = err.message;
      }
    },

    async getAssets() {
      try {
        const headers = { 'Content-Type': 'application/json' };
        const params = { 'name': 'Phillip Geeter' };

        const response = await axios({
          method: 'get',
          url: 'http://127.0.0.1:5000/get_assets',
          headers: headers,
          params: params,
        });

        console.log(response.data);

        this.data_getAssets = response.data;
        this.error = null;
      } catch (err) {
        this.data_getAssets = null;
        this.error = err.message;
      }
    },

    async createPerson() {
      try {
        const headers = { 'Content-Type': 'application/json' };

        const body = { 'name': 'Phillip Geeter',
                       'cash': 222,
                       'resource_dict': {'apple': 4} };

        const response = await axios({
          method: 'post',
          url: 'http://127.0.0.1:5000/create_person',
          headers: headers,
          data: body,
        });

        console.log(response.data);

        this.data_createPerson = response.data;
        this.error = null;
      } catch (err) {
        this.data_createPerson = null;
        this.error = err.message;
      }
    },

    async sell() {
      try {
        const headers = { 'Content-Type': 'application/json' };

        const body = { 'name': 'Phillip Geeter',
                       'resource_type': 'apple',
                       'amount': 1,
                       'price': 12 };

        const response = await axios({
          method: 'post',
          url: 'http://127.0.0.1:5000/sell',
          headers: headers,
          data: body,
        });

        console.log(response.data);

        this.data_sell = response.data;
        this.error = null;
      } catch (err) {
        this.data_sell = null;
        this.error = err.message;
      }
    },

    async buy() {
      try {
        const headers = { 'Content-Type': 'application/json' };

        const body = { 'name': 'Phillip Geeter',
                       'resource_type': 'apple',
                       'amount': 2 };

        const response = await axios({
          method: 'post',
          url: 'http://127.0.0.1:5000/buy',
          headers: headers,
          data: body,
        });

        console.log(response.data);

        this.data_buy = response.data;
        this.error = null;
      } catch (err) {
        this.data_buy = null;
        this.error = err.message;
      }
    },


  },

};



</script>



<template>

  <header>
    <img alt="Vue logo" class="logo" src="./assets/logo.svg" width="125" height="125" />
  </header>
  <br>


  <span>
    <button @click="getMarket" class="button_getMarket">Get Market</button>
    <div v-if="data_getMarket">
      <p>{{ data_getMarket.message }}</p>
    </div>
    <div v-if="error">
        <p>Error: {{ error }}</p>
    </div>
  </span>
  <br>


  <span>
    <button @click="getPrice" class="button_getPrice">Get Price</button>
    <div v-if="data_getPrice">
      <p>{{ data_getPrice.message }}</p>
    </div>
    <div v-if="error">
        <p>Error: {{ error }}</p>
    </div>
  </span>
  <br>


  <span>
    <button @click="getAssets" class="button_getAssets">Get Assets</button>
    <div v-if="data_getAssets">
      <p>{{ data_getAssets.message }}</p>
    </div>
    <div v-if="error">
        <p>Error: {{ error }}</p>
    </div>
  </span>
  <br>


  <span>
    <button @click="createPerson" class="button_createPerson">Create Person</button>
    <div v-if="data_createPerson">
      <p>{{ data_createPerson.message }}</p>
    </div>
    <div v-if="error">
        <p>Error: {{ error }}</p>
    </div>
  </span>
  <br>


  <span>
    <button @click="sell" class="button_sell">Sell</button>
    <div v-if="data_sell">
      <p>{{ data_sell.message }}</p>
    </div>
    <div v-if="error">
        <p>Error: {{ error }}</p>
    </div>
  </span>
  <br>


  <span>
    <button @click="buy" class="button_sell">Buy</button>
    <div v-if="data_buy">
      <p>{{ data_buy.message }}</p>
    </div>
    <div v-if="error">
        <p>Error: {{ error }}</p>
    </div>
  </span>
  <br>



</template>





<style scoped>
header {
  line-height: 1.5;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

.button_getMarket{
    height:20px;
    width:150px;
}

.button_createPerson{
    height:20px;
    width:150px;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
}
</style>
