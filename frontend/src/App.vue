
// npm run dev

<script>

import Listbox from 'primevue/listbox';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Message from 'primevue/message';

import axios from 'axios';


export default {


  components: {
    Listbox,
    InputText,
    Button,
    Message,
  },

  data() {
    return {
      data_getMarket: null,
      data_getPrice: null,
      data_getAssets: null,
      data_getPeople: null,

      data_createPerson: null,
      data_sell: null,
      data_buy: null,

      error: null,

      selectedPerson: '',
      newPersonName: '',
    };
  },

  mounted() {
    this.getPeople();
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

    async getPeople() {
      try {
        const headers = { 'Content-Type': 'application/json' };

        const response = await axios({
          method: 'get',
          url: 'http://127.0.0.1:5000/get_people',
          headers: headers,
        });

        console.log(response.data);

        this.data_getPeople = response.data;
        this.error = null;
      } catch (err) {
        this.data_getPeople = null;
        this.error = err.message;
      }
    },

    async createPerson(name) {
      try {
        const headers = { 'Content-Type': 'application/json' };

        const body = { 'name': String(name),
                       'cash': 0,
                       'resource_dict': {} };
                       // 'resource_dict': {'apple': 4} };

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

  <!-- <header>
    <img alt="Vue logo" class="logo" src="./assets/logo.svg" width="125" height="125" />
  </header>
  <br> -->


  <span>
    <!-- <button @click="getMarket" class="button_getMarket">Get Market</button> -->
    <Button type="submit" severity="secondary" label="Get Market" @click="getMarket" />
    <div v-if="data_getMarket">
      <pre>    {{ data_getMarket.message }}</pre>
    </div>
    <div v-if="error">
        <p>Error: {{ error }}</p>
    </div>
  </span>
  <br>


  <span>
    <!-- <button @click="getPrice" class="button_getPrice">Get Price</button> -->
    <Button type="submit" severity="secondary" label="Get Price" @click="getPrice" />
    <div v-if="data_getPrice">
      <pre>    {{ data_getPrice.message }}</pre>
    </div>
    <div v-if="error">
        <p>Error: {{ error }}</p>
    </div>
  </span>
  <br>


  <span>
    <!-- <button @click="getAssets" class="button_getAssets">Get Assets</button> -->
    <Button type="submit" severity="secondary" label="Get Assets" @click="getAssets" />
    <div v-if="data_getAssets">
      <pre>    {{ data_getAssets.message }}</pre>
    </div>
    <div v-if="error">
        <p>Error: {{ error }}</p>
    </div>
  </span>
  <br>


  <span>
    <!-- <button @click="getPeople" class="button_getPeople">Get People</button> -->
    <Button type="submit" severity="secondary" label="Get People" @click="getPeople" />
    <div v-if="data_getPeople">
      <pre>    {{ data_getPeople.message }}</pre>
    </div>
    <div v-if="error">
        <p>Error: {{ error }}</p>
    </div>
  </span>
  <br>


  <span>
    <!-- <button @click="createPerson" class="button_createPerson">Create Person</button> -->
    <Button type="submit" severity="secondary" label="Create Person" @click="createPerson('Phillip Geeter')" />
    <div v-if="data_createPerson">
      <pre>    {{ data_createPerson.message }}</pre>
    </div>
    <div v-if="error">
        <p>Error: {{ error }}</p>
    </div>
  </span>
  <br>


  <span>
    <!-- <button @click="sell" class="button_sell">Sell</button> -->
    <Button type="submit" severity="secondary" label="Sell" @click="sell" />
    <div v-if="data_sell">
      <pre>    {{ data_sell.message }}</pre>
    </div>
    <div v-if="error">
        <p>Error: {{ error }}</p>
    </div>
  </span>
  <br>


  <span>
    <!-- <button @click="buy" class="button_buy">Buy</button> -->
    <Button type="submit" severity="secondary" label="Buy" @click="buy" />
    <div v-if="data_buy">
      <pre>    {{ data_buy.message }}</pre>
    </div>
    <div v-if="error">
        <p>Error: {{ error }}</p>
    </div>
  </span>
  <br>


  <br>

  <div v-if="data_getPeople">
    <Listbox v-model="selectedPerson" :options="data_getPeople.data.people" filter class="w-full md:w-56" />
    <p>Selected value: {{ selectedPerson }}</p>
  </div>

  <br>

  <div class="flex flex-col gap-2">
    <!-- <label for="username">Username</label> -->
    <InputText type="text" v-model="newPersonName" placeholder="Name" />
    <Message size="small" severity="secondary" variant="simple">Create a new person</Message>
  </div>

  <div v-if="newPersonName">
    <Button type="submit" severity="secondary" label="Create New Person" @click="createPerson(newPersonName)" />
  </div>


  
</template>



<style scoped>
header {
  line-height: 1.5;
}

/*.logo {
  display: block;
  margin: 0 auto 2rem;
}*/

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  ./*logo {
    margin: 0 2rem 0 0;
  }*/

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
}
</style>
