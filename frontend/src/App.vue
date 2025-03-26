
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
      data_getResources: null,

      data_createPerson: null,
      data_sell: null,
      data_buy: null,
      data_cancelSell: null,

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
      selectedSaleForCancel: null,

      currentResource: null,
      selectedSale: null,
      data_getMarketForBuying: null,

      buyQuantity: null,
      numAvailable: null,
      pricePerUnit: null,

    };
  },

  mounted() {
    document.title = 'Market Simulator'; // set site title
    this.getResources();
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

      // if (this.currentPerson) {
      //   this.currentPersonSales = this.data_getMarket.data.sell_list.filter(x => x.name == this.currentPerson);
      // }
      // else {
      //   this.currentPersonSales = null;
      // }

    },

    async getPrice(resource_type, amount) {
      try {
        const headers = { 'Content-Type': 'application/json' };
        const params = { 'resource_type': resource_type,
                         'amount': amount };

        const response = await axios({
          method: 'get',
          url: 'http://127.0.0.1:5000/get_price',
          headers: headers,
          params: params,
        });

        console.log(response.data);

        this.data_getPrice = response.data;
        this.error = null;

        this.pricePerUnit = this.data_getPrice.data.price / amount;
        this.pricePerUnit = this.pricePerUnit.toFixed(2);

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

        this.money = this.data_getAssets.data.cash;

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


    async getResources() {
      try {
        const headers = { 'Content-Type': 'application/json' };

        const response = await axios({
          method: 'get',
          url: 'http://127.0.0.1:5000/get_resources',
          headers: headers,
        });

        console.log(response.data);

        this.data_getResources = response.data;
        this.error = null;
      } catch (err) {
        this.data_getResources = null;
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
        // await this.getMarket(resource_type)
        await this.getMarketForPerson(resource_type)


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

    async buy(name, resource_type, amount) {
      try {
        const headers = { 'Content-Type': 'application/json' };

        const body = { 'name': name,
                       'resource_type': resource_type,
                       'amount': amount };

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

      // refresh assets
      if (this.currentPerson) {
        await this.getAssets(this.currentPerson);
      }

      // reset
      this.buyQuantity = null;

    },


    async cancelSell(sell_id) {
      try {
        const headers = { 'Content-Type': 'application/json' };

        const body = { 'sell_id': sell_id };

        const response = await axios({
          method: 'post',
          url: 'http://127.0.0.1:5000/cancel_sell',
          headers: headers,
          data: body,
        });

        console.log(response.data);

        this.data_cancelSell = response.data;
        this.error = null;
      } catch (err) {
        this.data_cancelSell = null;
        this.error = err.message;
      }

      // refresh assets
      await this.getAssets(this.currentPerson);

      // refresh market
      await this.getMarketForPerson(this.selectedResource.resource)

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

      // reset
      this.selectedResource = null;
      this.currentPersonSales = null;


    },

    async getMarketForPerson(resource_type) {

      await this.getMarket(resource_type);

      if (this.currentPerson) {
        this.currentPersonSales = this.data_getMarket.data.sell_list.filter(x => x.name == this.currentPerson);
      }
      else {
        this.currentPersonSales = null;
      }

      // reset
      this.selectedSaleForCancel = null;
    },


    async getMarketForBuying(resource_type) {

      await this.getMarket(resource_type);

      this.data_getMarketForBuying = this.data_getMarket;

      // Add up all the quantities to get total number for sale
      var num_available = 0;
      for (let i = 0; i < this.data_getMarketForBuying.data.sell_list.length; i++) {
        num_available += this.data_getMarketForBuying.data.sell_list[i].amount;
      }

      this.numAvailable = num_available;

      // reset
      this.buyQuantity = null;

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
          <span class="p-2 relative text-lg" >Money: &nbsp; ${{money.toFixed(2)}}</span>
        </div>



        <div v-if="data_getAssets">

          <DataTable selectionMode="single" v-model:selection="selectedResource" :value="data_getAssets.data.resource_list" size="small" scrollable scrollHeight="400px" tableStyle="min-width: 10rem" @row-select="getMarketForPerson(selectedResource.resource)" >
            <Column field="resource" header="Resource"></Column>
            <Column field="quantity" header="Quantity"></Column>
          </DataTable>

        </div>


        <div v-if="selectedResource">

          <p class="relative text-xl text-center">{{selectedResource.resource}}</p>

            <InputNumber v-model="sellQuantity" inputId="integeronly" placeholder="Sell quantity" fluid :model-value="sellQuantity" @input="(e) => (sellQuantity = e.value)" />

            <InputNumber v-model="sellPrice" inputId="price_input" mode="currency" currency="USD" placeholder="Sell price" fluid :model-value="sellPrice" @input="(e) => (sellPrice = e.value)" />

            <div v-if="sellQuantity && sellPrice">
              <Button style="width: 100%;" type="submit" severity="secondary" label="Submit" @click="sell(currentPerson, selectedResource.resource, sellQuantity, sellPrice)" />
            </div>

            <div v-if="currentPersonSales">
              <p class="relative text-xl text-center">Selling</p>

              <DataTable selectionMode="single" v-model:selection="selectedSaleForCancel" :value="currentPersonSales" size="small" scrollable scrollHeight="400px" tableStyle="min-width: 10rem" >
                <Column field="amount" header="Quantity"></Column>
                <Column field="price" header="Price"></Column>
              </DataTable>

              <div v-if="selectedSaleForCancel" >
                <Button style="width: 100%;" type="submit" severity="secondary" label="Cancel listing" @click="cancelSell(selectedSaleForCancel.sell_id)" />
              </div>

            </div>

        </div>



      </div>




      <div class="flexbox-item flexbox-item-2">

        <div v-if="currentResource">
          <p class="relative text-xl text-center">Resource: {{ currentResource }}</p>
        </div>
        <div v-else>
          <p class="relative text-xl text-center">Select a resource</p>
        </div>

        <div v-if="data_getResources">
          <Select v-model="currentResource" :options="data_getResources.data.resources" placeholder="Select resource" class="w-full md:w-56" filter @update:modelValue="getMarketForBuying(currentResource)"/>
        </div>

        <div v-if="currentResource && data_getMarketForBuying && currentPerson">

          <p class="relative text-xl text-center">Available: {{numAvailable}}</p>

          <InputNumber v-model="buyQuantity" inputId="integeronly" placeholder="Buy quantity" fluid @update:modelValue="getPrice(currentResource, buyQuantity)" />

          <div v-if="buyQuantity && data_getPrice && data_getPrice.data.price">
            <span class="p-2 relative text-lg" >Total Price: &nbsp; ${{data_getPrice.data.price.toFixed(2)}} &nbsp; &nbsp; Unit Price &nbsp; ${{pricePerUnit}}</span>

            <div v-if="(money != null) && (money >= data_getPrice.data.price)">
              <Button style="width: 100%;" type="submit" severity="secondary" label="Submit" @click="buy(currentPerson, currentResource, buyQuantity)" />
            </div>

          </div>


        </div>
        

      </div>



      <div class="flexbox-item flexbox-item-3">

          <Button type="submit" severity="secondary" label="Get Market" @click="getMarket('apple')" />
          <div v-if="data_getMarket">
            <pre>    {{ data_getMarket.message }}</pre>
          </div>
          <div v-else><br></div>


          <Button type="submit" severity="secondary" label="Get Price" @click="getPrice('apple', 1)" />
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


          <Button type="submit" severity="secondary" label="Buy" @click="buy('Phillip Geeter', 'apple', 2)" />
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
