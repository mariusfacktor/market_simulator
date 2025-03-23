
// npm run dev

<script>

import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Message from 'primevue/message';
import Select from 'primevue/select';

import axios from 'axios';


export default {


  components: {
    InputText,
    Button,
    Message,
    Select,
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
      createdPerson: '',
      currentPerson: '',

      selectPersonButton: null,
      createPersonButton: null,

      money: null,
    };
  },

  mounted() {
    document.title = 'Market Simulator'; // set site title
    // this.getPeople();
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

    async getAssets(name) {
      try {
        const headers = { 'Content-Type': 'application/json' };
        const params = { 'name': String(name) };

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

      // set currentPerson
      this.setCurrentPerson(name);

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


    async buttonSelectPerson() {

      if (this.selectPersonButton) {
        this.selectPersonButton = false;
        this.createPersonButton = false;
      }
      else {

        this.getPeople()

        this.selectPersonButton = true;
        this.createPersonButton = false;
      }
    },

    async buttonCreatePerson() {
      if (this.createPersonButton) {
        this.selectPersonButton = false;
        this.createPersonButton = false;
      }
      else {
        this.selectPersonButton = false;
        this.createPersonButton = true;
      }
    },


    async setCurrentPerson(name) {
      this.currentPerson = name;
      await this.getAssets(name);
      this.money = this.data_getAssets.data.cash;

      console.log(this.money);
    },

 


  },

};



</script>





<template>


  <body>





    <div class="flexbox-container-top">
      <div class="flexbox-item flexbox-item-4">


      </div>
    </div>







    <div class="flexbox-container">
      <div class="flexbox-item flexbox-item-1">

        <div v-if="currentPerson">
          <p class="relative text-xl text-center">Name: {{ currentPerson }}</p>
        </div>
        <div v-else>
          <p class="relative text-xl text-center">Select or create a person</p>
        </div>


        <Button type="submit" severity="secondary" label="Select person" @click="buttonSelectPerson()" />
        <div class="p-10 inline-block">
          <Button type="submit" severity="secondary" label="Create new person" @click="buttonCreatePerson()" />
        </div>



        <div v-if="selectPersonButton">

          <div v-if="data_getPeople">
            <Select v-model="selectedPerson" :options="data_getPeople.data.people" placeholder="Select person" class="w-full md:w-56" filter @update:modelValue="setCurrentPerson(selectedPerson)"/>
          </div>

        </div>




        <div v-if="createPersonButton">

          <div class="flex flex-col gap-2">
            <InputText type="text" v-model="createdPerson" placeholder="Name" />
            <Message size="small" severity="secondary" variant="simple"></Message>
          </div>

          <div v-if="createdPerson">
            <Button type="submit" severity="secondary" label="Submit new person" @click="createPerson(createdPerson)" />
          </div>

        </div>


        <br>
        <p class="relative text-xl text-center">Assets</p>

        <div v-if="money != null">
          <!-- <p class="p-10">Money: ${{money}}</p> -->
          <span class="p-10">Money: ${{money}}</span>
        </div>


      </div>

      <div class="flexbox-item flexbox-item-2"></div>

      <div class="flexbox-item flexbox-item-3">

          <Button type="submit" severity="secondary" label="Get Market" @click="getMarket" />
          <div v-if="data_getMarket">
            <pre>    {{ data_getMarket.message }}</pre>
          </div>
          <div v-else><br></div>


          <Button type="submit" severity="secondary" label="Get Price" @click="getPrice" />
          <div v-if="data_getPrice">
            <pre>    {{ data_getPrice.message }}</pre>
          </div>
          <div v-else><br></div>


          <Button type="submit" severity="secondary" label="Get Assets" @click="getAssets('Phillip Geeter')" />
          <div v-if="data_getAssets">
            <pre>    {{ data_getAssets.message }}</pre>
          </div>
          <div v-else><br></div>


          <Button type="submit" severity="secondary" label="Get People" @click="getPeople" />
          <div v-if="data_getPeople">
            <pre>    {{ data_getPeople.message }}</pre>
          </div>
          <div v-else><br></div>


          <Button type="submit" severity="secondary" label="Create Person" @click="createPerson('Phillip Geeter')" />
          <div v-if="data_createPerson">
            <pre>    {{ data_createPerson.message }}</pre>
          </div>
          <div v-else><br></div>


          <Button type="submit" severity="secondary" label="Sell" @click="sell" />
          <div v-if="data_sell">
            <pre>    {{ data_sell.message }}</pre>
          </div>
          <div v-else><br></div>


          <Button type="submit" severity="secondary" label="Buy" @click="buy" />
          <div v-if="data_buy">
            <pre>    {{ data_buy.message }}</pre>
          </div>
          <div v-else><br></div>



      </div>

    </div>

  </body>


  
</template>



<style scoped>


.flexbox-container-top {
  display: flex;
  justify-content: space-around;
  height: 20vh;
  width: 90vw;
}

.flexbox-container {
  display: flex;
  justify-content: space-around;
  height: 80vh;
  width: 90vw;
}

.flexbox-item {
  width: 300px;
  margin: 8px;
  border: 3px solid #333;
  background-color: #dfdfdf;
}

.flexbox-item-1 {
  flex-grow: 1;
}

.flexbox-item-2 {
  flex-grow: 1;
}

.flexbox-item-3 {
  flex-grow: 1;
}

.flexbox-item-4 {
  flex-grow: 1;
}



</style>
