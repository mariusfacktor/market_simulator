
// npm run dev

<script>

import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Message from 'primevue/message';
import Select from 'primevue/select';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import SelectButton from 'primevue/selectbutton';
import InputNumber from 'primevue/inputnumber';

import axios from 'axios';




export default {


  components: {
    InputText,
    Button,
    Message,
    Select,
    DataTable,
    Column,
    SelectButton,
    InputNumber,
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
      selectButtonPerson: null,

      money: null,
      selectedResource: null,
      sellQuantity: null,
      sellPrice: null,

      currentPersonSales: null,
    };
  },

  mounted() {
    document.title = 'Market Simulator'; // set site title
    // this.getPeople();
  },

  methods: {

    async getMarket(resource_type) {
      try {
        const headers = { 'Content-Type': 'application/json' };
        const params = { 'resource_type': resource_type };

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

      if (this.currentPerson) {
        this.currentPersonSales = this.data_getMarket.data.sell_list.filter(x => x.name == this.currentPerson);
      }
      else {
        this.currentPersonSales = null;
      }

      // console.log([...this.currentPersonSales]);

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

    async sell(name, resource_type, amount, price) {
      try {
        const headers = { 'Content-Type': 'application/json' };

        const body = { 'name': name,
                       'resource_type': resource_type,
                       'amount': amount,
                       'price': price };

        const response = await axios({
          method: 'post',
          url: 'http://127.0.0.1:5000/sell',
          headers: headers,
          data: body,
        });

        console.log(response.data);

        // get updated list of resources
        await this.getAssets(name);

        // get updated market
        await this.getMarket(resource_type)

        // reset fields
        this.sellQuantity = null;
        this.sellPrice = null;
        // this.selectedResource = null;

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


    async buttonSelectOrCreatePerson(name) {

      if (name == 'Select person') {

        this.selectPersonButton = true;
        this.createPersonButton = false;
        this.getPeople()
        }
      else if (name == 'Create person') {

        this.selectPersonButton = false;
        this.createPersonButton = true;
      }
      else {
        this.selectPersonButton = false;
        this.createPersonButton = false;
      }
    },


    async setCurrentPerson(name) {
      this.currentPerson = name;

      await this.getAssets(name);
      this.money = this.data_getAssets.data.cash;

      // reset
      this.selectedResource = null;
      this.currentPersonSales = null;


    },



    async debugFunc() {
      console.log('DEBUG A0')
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


        <SelectButton v-model="selectButtonPerson" @click="buttonSelectOrCreatePerson(selectButtonPerson)" :options="['Select person', 'Create person']" />


        <div v-if="selectPersonButton">

          <div v-if="data_getPeople">
            <Select v-model="selectedPerson" :options="data_getPeople.data.people" placeholder="Select person" class="w-full md:w-56" filter @update:modelValue="setCurrentPerson(selectedPerson)"/>
          </div>

        </div>




        <div v-if="createPersonButton" style="width: 100%">

          <InputText type="text" v-model="createdPerson" placeholder="Name" style="width: 100%;" />

          <div v-if="createdPerson">
            <Button style="width: 100%;" type="submit" severity="secondary" label="Submit" @click="createPerson(createdPerson)" />
          </div>

        </div>



        <div v-if="money != null">
          <p class="relative text-xl text-center">Assets</p>
          <span class="p-2 relative text-lg" >Money: &nbsp; ${{money}}</span>
        </div>



        <div v-if="data_getAssets">
          <DataTable selectionMode="single" v-model:selection="selectedResource" :value="data_getAssets.data.resource_list" size="small" scrollable scrollHeight="400px" tableStyle="min-width: 10rem" @row-select="getMarket(selectedResource.resource)" >
            <Column field="resource" header="Resource"></Column>
            <Column field="quantity" header="Quantity"></Column>
          </DataTable>
        </div>

        <div v-if="selectedResource">

          <p class="relative text-xl text-center">{{selectedResource.resource}}</p>

            <InputNumber v-model="sellQuantity" inputId="integeronly" placeholder="Sell quantity" fluid :model-value="sellQuantity" @input="(e) => (sellQuantity = e.value)" />

            <InputNumber v-model="sellPrice" inputId="integeronly" placeholder="Sell price" fluid :model-value="sellPrice" @input="(e) => (sellPrice = e.value)" />

            <div v-if="sellQuantity && sellPrice">
              <Button style="width: 100%;" type="submit" severity="secondary" label="Submit" @click="sell(currentPerson, selectedResource.resource, sellQuantity, sellPrice)" />
            </div>

            <div v-if="currentPersonSales">
              <p class="relative text-xl text-center">Selling</p>

              <DataTable selectionMode="single" v-model:selection="selectedResource" :value="currentPersonSales" size="small" scrollable scrollHeight="400px" tableStyle="min-width: 10rem" >
                <Column field="amount" header="Quantity"></Column>
                <Column field="price" header="Price"></Column>
              </DataTable>

            </div>

        </div>



      </div>




      <div class="flexbox-item flexbox-item-2"></div>



      <div class="flexbox-item flexbox-item-3">

          <Button type="submit" severity="secondary" label="Get Market" @click="getMarket('apple')" />
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


          <Button type="submit" severity="secondary" label="Sell" @click="sell('Phillip Geeter', 'apple', 2, 8)" />
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
